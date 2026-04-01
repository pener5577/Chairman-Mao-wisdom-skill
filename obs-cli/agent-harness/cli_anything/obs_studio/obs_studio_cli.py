#!/usr/bin/env python3
"""
OBS Studio CLI - A stateful command-line interface for OBS Studio

This CLI provides full OBS Studio control capabilities via WebSocket.
No OBS running? No problem - simulates scene structure for planning.

Usage:
    # One-shot commands
    obs-cli scene list
    obs-cli scene add --name "Gaming"
    obs-cli recording start
    obs-cli recording stop

    # Interactive REPL (default)
    obs-cli
"""

import sys
import os
import json
import click
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli_anything.obs_studio.core.session import Session
from cli_anything.obs_studio.core import scenes as scene_mod
from cli_anything.obs_studio.core import sources as src_mod
from cli_anything.obs_studio.core import recording as rec_mod
from cli_anything.obs_studio.core import streaming as stream_mod

# Global session state
_session: Optional[Session] = None
_json_output = False
_repl_mode = False


def get_session() -> Session:
    """Get or create the global session"""
    global _session
    if _session is None:
        _session = Session()
    return _session


def output(data, message: str = ""):
    """Output in human-readable or JSON format"""
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)
        else:
            click.echo(str(data))


def _print_dict(d: dict, indent: int = 0):
    """Pretty print a dictionary"""
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{prefix}{k}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{k}:")
            _print_list(v, indent + 1)
        else:
            click.echo(f"{prefix}{k}: {v}")


def _print_list(items: list, indent: int = 0):
    """Pretty print a list"""
    prefix = "  " * indent
    for i, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{prefix}[{i}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}- {item}")


def handle_error(func):
    """Error handling decorator"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": "file_not_found"}))
            else:
                click.echo(f"❌ Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
        except (ValueError, IndexError, RuntimeError) as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"❌ Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": "unknown"}))
            else:
                click.echo(f"❌ Unexpected error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
    return wrapper


@click.group(invoke_without_command=True)
@click.option('--json', 'json_output', is_flag=True, help='Output JSON format')
@click.option('--host', default='localhost', help='OBS WebSocket host')
@click.option('--port', default=4455, help='OBS WebSocket port')
@click.option('--password', default='', help='OBS WebSocket password')
@click.pass_context
def cli(ctx, json_output, host, port, password):
    """OBS Studio CLI - Control OBS via command line or REPL"""
    global _json_output, _repl_mode
    _json_output = json_output
    
    ctx.ensure_object(dict)
    ctx.obj['host'] = host
    ctx.obj['port'] = port
    ctx.obj['password'] = password
    ctx.obj['connected'] = False
    
    # Try to connect to OBS
    session = get_session()
    session.configure(host, port, password)
    
    # If no subcommand, enter REPL
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


@cli.command()
@click.pass_context
def repl(ctx):
    """Enter interactive REPL mode"""
    global _repl_mode
    _repl_mode = True
    
    session = get_session()
    
    click.echo("🎬 OBS Studio CLI - REPL Mode")
    click.echo("=" * 40)
    click.echo(f"Host: {ctx.obj['host']}:{ctx.obj['port']}")
    
    if session.connected:
        click.echo("✅ Connected to OBS")
    else:
        click.echo("⚠️  Not connected (OBS not running?)")
        click.echo("   Running in simulation mode")
    
    click.echo("\nType 'help' for commands, 'exit' to quit")
    click.echo("-" * 40)
    
    # Simple REPL loop
    while True:
        try:
            cmd = input("obs> ").strip()
            if not cmd:
                continue
            if cmd == 'exit' or cmd == 'quit':
                break
            elif cmd == 'help':
                _show_help()
            elif cmd == 'status':
                ctx.invoke(status)
            elif cmd == 'scenes':
                ctx.invoke(scenes)
            elif cmd.startswith('scene '):
                parts = cmd.split(' ', 2)
                if len(parts) >= 2:
                    ctx.invoke(scene, name=parts[1])
            else:
                click.echo(f"Unknown command: {cmd}")
        except (KeyboardInterrupt, EOFError):
            break
    
    click.echo("\n👋 Goodbye!")


def _show_help():
    """Show help for REPL mode"""
    click.echo("""
Available commands:
  status          - Show OBS status
  scenes          - List all scenes
  scene <name>    - Switch to scene
  recording start - Start recording
  recording stop  - Stop recording
  streaming start - Start streaming
  streaming stop  - Stop streaming
  sources         - List sources in current scene
  help            - Show this help
  exit            - Exit REPL
""")


# ==================== Status Commands ====================

@cli.command()
@click.pass_context
def status(ctx):
    """Show OBS status"""
    session = get_session()
    data = session.get_status()
    output(data, "📊 OBS Status:")


@cli.command()
@click.pass_context
def scenes(ctx):
    """List all scenes"""
    session = get_session()
    data = session.get_scenes()
    if isinstance(data, dict) and 'scenes' in data:
        output(data['scenes'], "🎬 Scenes:")
        if 'current' in data:
            click.echo(f"\n✅ Current: {data['current']}")
    else:
        output(data)


@cli.command()
@click.argument('name')
@click.pass_context
def scene(ctx, name):
    """Switch to a scene"""
    session = get_session()
    result = session.switch_scene(name)
    if result:
        output({"success": True, "scene": name}, f"✅ Switched to scene: {name}")
    else:
        output({"success": False, "error": "Scene not found"}, f"❌ Failed to switch to: {name}")


# ==================== Recording Commands ====================

@cli.command()
@click.pass_context
def recording_start(ctx):
    """Start recording"""
    session = get_session()
    result = session.start_recording()
    if result:
        output({"success": True}, "🔴 Recording started")
    else:
        output({"success": False}, "❌ Failed to start recording")


@cli.command()
@click.pass_context
def recording_stop(ctx):
    """Stop recording"""
    session = get_session()
    result = session.stop_recording()
    if result:
        output({"success": True}, "⏹️ Recording stopped")
    else:
        output({"success": False}, "❌ Failed to stop recording")


@cli.command()
@click.pass_context
def recording_status(ctx):
    """Check recording status"""
    session = get_session()
    data = session.get_recording_status()
    if data.get('recording'):
        output(data, "🔴 Recording in progress")
        if 'duration' in data:
            output(data, f"⏱️ Duration: {data['duration']}")
    else:
        output(data, "⏸️ Not recording")


# ==================== Streaming Commands ====================

@cli.command()
@click.pass_context
def streaming_start(ctx):
    """Start streaming"""
    session = get_session()
    result = session.start_streaming()
    if result:
        output({"success": True}, "📡 Streaming started")
    else:
        output({"success": False}, "❌ Failed to start streaming")


@cli.command()
@click.pass_context
def streaming_stop(ctx):
    """Stop streaming"""
    session = get_session()
    result = session.stop_streaming()
    if result:
        output({"success": True}, "⏹️ Streaming stopped")
    else:
        output({"success": False}, "❌ Failed to stop streaming")


@cli.command()
@click.pass_context
def streaming_status(ctx):
    """Check streaming status"""
    session = get_session()
    data = session.get_streaming_status()
    if data.get('streaming'):
        output(data, "📡 Currently streaming")
    else:
        output(data, "⏸️ Not streaming")


# ==================== Source Commands ====================

@cli.command()
@click.pass_context
def sources(ctx):
    """List sources in current scene"""
    session = get_session()
    data = session.get_sources()
    if isinstance(data, dict) and 'sources' in data:
        output(data['sources'], "📺 Sources in current scene:")
    else:
        output(data)


@cli.command()
@click.argument('name')
@click.argument('type')
@click.pass_context
def source_add(ctx, name, type):
    """Add a source to current scene"""
    session = get_session()
    result = session.add_source(name, type)
    if result:
        output({"success": True, "source": name, "type": type}, f"✅ Added source: {name} ({type})")
    else:
        output({"success": False}, f"❌ Failed to add source: {name}")


# ==================== Scene Collection Commands ====================

@cli.command()
@click.argument('name')
@click.pass_context
def project_new(ctx, name):
    """Create a new scene collection"""
    session = get_session()
    result = session.create_project(name)
    if result:
        output({"success": True, "project": name}, f"✅ Created scene collection: {name}")
    else:
        output({"success": False}, f"❌ Failed to create: {name}")


@cli.command()
@click.pass_context
def projects(ctx):
    """List all scene collections"""
    session = get_session()
    data = session.get_projects()
    if isinstance(data, dict) and 'projects' in data:
        output(data['projects'], "📁 Scene Collections:")
    else:
        output(data)


# ==================== Utility Commands ====================

@cli.command()
@click.pass_context
def quit(ctx):
    """Exit the CLI"""
    sys.exit(0)


def main():
    """Entry point"""
    cli(obj={})


if __name__ == '__main__':
    main()
