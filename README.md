# Task Manager MCP Server

Simple setup guide for running this MCP server on **Windows** with the **Claude Microsoft Store app**.

This README is based on real issues faced during setup, so you can avoid the same errors.

## Why this guide exists

Some default MCP install flows did not work reliably with the Store version of Claude on this machine.  
The stable approach was:

- create a local `.venv`
- install MCP using `pip` inside that venv
- manually add MCP server config to Claude config files

## Prerequisites

- Windows
- Python installed
- `uv` installed
- Claude desktop app (Microsoft Store version)

## Setup

### 1) Create and open your project folder

```powershell
mkdir C:\path\to\my-new-mcp
cd C:\path\to\my-new-mcp
```

### 2) Create virtual environment

```powershell
uv venv
```

### 3) Prepare pip inside `.venv`

```powershell
.\.venv\Scripts\python -m ensurepip --upgrade
.\.venv\Scripts\python -m pip install --upgrade pip setuptools wheel
```

### 4) Install MCP (with CLI extras)

```powershell
.\.venv\Scripts\python -m pip install "mcp[cli]"
```

### 5) Add server code (`main.py`)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool()
# Sample Function 

if __name__ == "__main__":
    mcp.run()
```

### 6) Register server in Claude config

Add this entry under `mcpServers`:

```json
{
  "mcpServers": {
    "MyServer": {
      "command": "C:\\path\\to\\my-new-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\path\\to\\my-new-mcp\\main.py"
      ]
    }
  }
}
```

Update both of these files:

- `C:\Users\User123\AppData\Roaming\Claude\claude_desktop_config.json`
- `C:\Users\User123\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`

### 7) Restart Claude completely

```powershell
Get-Process Claude -ErrorAction SilentlyContinue | Stop-Process -Force
```

Now open Claude again.

### 8) Validate

In Claude chat, ask it to call `ping`.  
Expected response: `pong`.

## Common problems and quick fixes

- **`uv run mcp install main.py` says Claude not found**  
  Auto-detection may miss the Store app path. Use manual config as shown above.

- **`uv add mcp` fails with Access denied (`os error 5`)**  
  Usually a uv cache permission/lock issue. Installing with `pip` inside `.venv` is more reliable.

- **`mcp --help` says typer is required**  
  Install `mcp[cli]`, not just base `mcp`.

- **`python main.py` prints nothing**  
  Normal behavior for MCP stdio servers; they wait quietly for incoming tool calls.
