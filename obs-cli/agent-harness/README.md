# OBS Studio CLI

A stateful command-line interface for OBS Studio - Built with CLI-Anything methodology.

## Features

- 🎬 **Scene Management** - List, add, switch scenes
- 🔴 **Recording Control** - Start/stop recording
- 📡 **Streaming Control** - Start/stop streaming
- 📺 **Source Management** - Add/remove sources
- 💾 **Scene Collections** - Create and manage projects
- 🔌 **WebSocket Mode** - Control real OBS Studio
- 🎭 **Simulation Mode** - Works even when OBS isn't running

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Enter interactive REPL
obs-cli

# List scenes
obs-cli scenes

# Start recording
obs-cli recording start

# Switch scene
obs-cli scene Gaming
```

## Commands

| Command | Description |
|---------|-------------|
| `obs-cli scenes` | List all scenes |
| `obs-cli scene <name>` | Switch to scene |
| `obs-cli recording start` | Start recording |
| `obs-cli recording stop` | Stop recording |
| `obs-cli streaming start` | Start streaming |
| `obs-cli streaming stop` | Stop streaming |
| `obs-cli sources` | List sources |
| `obs-cli status` | Show full status |

## Options

```bash
obs-cli --host 192.168.1.100 --port 4455 --password secret
obs-cli --json  # JSON output for scripting
```

## Requirements

- Python 3.10+
- OBS Studio (optional, works in simulation mode)
- OBS WebSocket plugin (optional, for real OBS control)

## Built with CLI-Anything

This project follows the [CLI-Anything](https://github.com/HKUDS/CLI-Anything) methodology
for creating agent-native CLI interfaces.
