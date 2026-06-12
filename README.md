# Window Control Tool

[![Build](https://github.com/DynamycSound/window_control_tool/actions/workflows/build.yml/badge.svg)](https://github.com/DynamycSound/window_control_tool/actions/workflows/build.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-0078d7.svg)](#requirements)

Move, resize and restyle **any window** on Windows with simple global hotkeys —
no mouse needed. Comes with a clean, modern dark/light GUI where you can tune
everything and see what's happening in real time.

## ✨ Features

- **Move windows** with the arrow keys — pixel-precise, configurable step size
- **Resize windows** with `Shift + Arrow keys`
- **Change opacity** of any window with `Ctrl + Up / Down`
- **Always on top** toggle with `Ctrl + Left / Right`
- **Send a window to the next monitor** with `Ctrl + Shift + M`
- Modern GUI with dark, light and system themes
- Built-in hotkey reference, activity log and settings — no popups
- Settings persist automatically between sessions

## ⌨️ Hotkeys

| Hotkey | Action |
| --- | --- |
| `↑ ↓ ← →` | Move the focused window |
| `Shift + ↑ ↓ ← →` | Resize the window (grow that edge) |
| `Ctrl + ↑` | Increase opacity |
| `Ctrl + ↓` | Decrease opacity |
| `Ctrl + →` | Set always on top |
| `Ctrl + ←` | Remove always on top |
| `Ctrl + Shift + M` | Move window to the next monitor |

Hotkeys always act on the window that currently has focus, and only while the
switch in the app is turned **on**.

## 🚀 Getting started

### Option 1 — Download the exe (easiest)

1. Grab `WindowControlTool.exe` from the
   [latest release](https://github.com/DynamycSound/window_control_tool/releases/latest).
2. Run it. Flip the switch. Done — no Python required.

> **Note:** Because the exe registers global hotkeys, some antivirus tools may
> flag it. The app is fully open source — you can read every line of code in
> this repository or build the exe yourself (see below).

### Option 2 — Run from source

Requires Python 3.9+ on Windows.

```bash
git clone https://github.com/DynamycSound/window_control_tool.git
cd window_control_tool
pip install -r requirements.txt
pip install -e .
python -m window_control_tool
```

*(Alternatively, if you do not want to install it locally, you can set the Python path environment variable before running: `$env:PYTHONPATH="src"; python -m window_control_tool` in PowerShell.)*

### Build the exe yourself

To build a working executable without import errors, create a temporary file named `run.py` in the root directory with this content:

```python
from window_control_tool.gui import run
if __name__ == "__main__":
    run()
```

Then, compile the executable by pointing PyInstaller to `run.py` and referencing the `src` directory:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name WindowControlTool \
  --paths src --collect-all customtkinter run.py
```

The working exe will appear in the `dist/` folder. You can safely delete `run.py` after the build is complete.

## 🖥️ Requirements

- Windows 10 / 11 (the win32 APIs the tool uses are Windows-only)
- Python 3.9+ if running from source

## ⚙️ Configuration

Everything is configurable from the **Settings** page in the app:

- **Move / resize step** — pixels per key press (default 40)
- **Opacity change per press** — 10 / 25 / 50
- **Appearance** — dark, light or follow the system
- **Auto-enable hotkeys** when the app starts

Settings are stored in `%APPDATA%\WindowControlTool\settings.json`.

## 🤝 Contributing

Contributions are welcome! Please read
[CONTRIBUTING.md](CONTRIBUTING.md) for how to set up a dev environment, the
code style, and how to submit pull requests. Bug reports and feature ideas go
in the [issue tracker](https://github.com/DynamycSound/window_control_tool/issues).

## 📄 License

This project is free and open source under the [MIT License](LICENSE) —
you may use, copy, modify and redistribute it, commercially or not.

---

Made by **Stefan M. (DynamycSound)**
