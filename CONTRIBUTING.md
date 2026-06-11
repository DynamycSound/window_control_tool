# Contributing to Window Control Tool

Thanks for your interest in contributing! All kinds of contributions are
welcome: bug reports, feature ideas, documentation fixes and code.

## Reporting bugs / requesting features

- Use the [issue templates](https://github.com/DynamycSound/window_control_tool/issues/new/choose).
- For bugs, include your Windows version, Python version (if running from
  source), and steps to reproduce.

## Development setup

```bash
git clone https://github.com/DynamycSound/window_control_tool.git
cd window_control_tool
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install ruff
python -m window_control_tool
```

The codebase lives in `src/window_control_tool/`:

| File | Purpose |
| --- | --- |
| `gui.py` | The CustomTkinter GUI (pages, navigation, activity log) |
| `hotkeys.py` | Global hotkey registration and the hotkey reference table |
| `window_actions.py` | The actual win32 window operations |
| `config.py` | Settings persistence (`%APPDATA%\WindowControlTool`) |

## Code style

- Run `ruff check src` before committing — CI runs the same check.
- Keep functions small and prefer plain, readable code over cleverness.
- All win32 calls belong in `window_actions.py`; hotkey actions must never
  raise (wrap risky calls so the listener keeps running).

## Pull requests

1. Fork the repo and create a branch from `main`.
2. Make your change, test it on Windows if it touches window behaviour.
3. Update the README / hotkey reference if you change user-facing behaviour.
4. Open a PR with a clear description of what and why.

Small, focused PRs are much easier to review than large ones.

## License

By contributing, you agree that your contributions will be licensed under the
[MIT License](LICENSE).
