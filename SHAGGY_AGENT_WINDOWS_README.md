# Shaggy Agent Windows Install Package

This folder is a branded Shaggy Agent copy of the open-source Shaggy Agent engine.

## Install on a Windows laptop

1. Unzip the package.
2. Right-click `INSTALL-SHAGGY-AGENT-WINDOWS.cmd` and choose **Run as administrator** if your laptop policy requires it. Normal user mode is usually enough.

Or run from PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\install-shaggy-agent-windows.ps1
```

## After install

Open a new PowerShell window and run:

```powershell
shaggy setup
shaggy doctor
shaggy
```

## What it installs

- Local app folder: `%LOCALAPPDATA%\ShaggyAgent`
- Agent data folder: `%LOCALAPPDATA%\ShaggyAgent\data`
- Python virtual environment: `%LOCALAPPDATA%\ShaggyAgent\.venv`
- Commands added to PATH:
  - `shaggy`
  - `shaggy-agent`

## Notes

- This package does **not** include Rahim's Mac secrets, API keys, Telegram tokens, Google auth, or business memory.
- Each Windows laptop must run `shaggy setup` and add its own model/API credentials.
- The code keeps some internal module names from Shaggy for compatibility, but user-facing branding and install commands are Shaggy Agent.
- Original engine license: MIT / Cherries and Co Shaggy Agent.
