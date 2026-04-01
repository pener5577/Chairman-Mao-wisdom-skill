---
name: obs-cli
description: "Use OBS Studio CLI to control recording, streaming, scenes, and sources. Triggers: obs, obs-cli, obs studio, recording, streaming, scenes, sources"
---

# OBS Studio CLI Skill

## Overview

OBS CLI provides command-line control for OBS Studio via WebSocket or simulation mode.

## Commands

### Scene Management
```bash
obs-cli scenes                    # List all scenes
obs-cli scene <name>             # Switch to scene
obs-cli scene add --name <name> # Add new scene
```

### Recording
```bash
obs-cli recording start          # Start recording
obs-cli recording stop          # Stop recording
obs-cli recording status        # Check status
```

### Streaming
```bash
obs-cli streaming start          # Start streaming
obs-cli streaming stop          # Stop streaming
obs-cli streaming status        # Check status
```

### Sources
```bash
obs-cli sources                 # List sources in current scene
obs-cli source add <name> <type> # Add source to scene
```

### Project/Scene Collections
```bash
obs-cli projects                # List all scene collections
obs-cli project new <name>     # Create new scene collection
```

### Interactive Mode
```bash
obs-cli                        # Enter REPL mode (default)
obs-cli --json                 # JSON output mode
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--host` | OBS WebSocket host | localhost |
| `--port` | OBS WebSocket port | 4455 |
| `--password` | OBS WebSocket password | (none) |
| `--json` | Output JSON format | false |

## Requirements

- OBS Studio with WebSocket plugin enabled
- Python 3.10+
- `websocket-client` Python package

## Installation

```bash
pip install -e .
```

## Examples

### Start Recording
```bash
obs-cli recording start
```

### Switch Scene
```bash
obs-cli scene "Gaming"
```

### Check Status
```bash
obs-cli status --json
```
