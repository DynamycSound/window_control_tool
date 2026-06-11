"""Persistent user settings.

Settings are stored as JSON in the per-user application data directory
(%APPDATA%\\WindowControlTool on Windows, ~/.config/window-control-tool
elsewhere) so the installed/portable exe never needs write access to its
own folder.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

DEFAULT_MOVE_STEP = 40
DEFAULT_OPACITY_STEP = 25


def _config_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "WindowControlTool"
    return Path.home() / ".config" / "window-control-tool"


CONFIG_FILE = _config_dir() / "settings.json"


@dataclass
class Settings:
    move_step: int = DEFAULT_MOVE_STEP
    opacity_step: int = DEFAULT_OPACITY_STEP
    appearance_mode: str = "dark"  # "dark", "light" or "system"
    start_hotkeys_on_launch: bool = False
    accent_theme: str = "blue"
    extra: dict = field(default_factory=dict)

    @classmethod
    def load(cls) -> "Settings":
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return cls()
        known = {f for f in cls.__dataclass_fields__ if f != "extra"}
        kwargs = {k: v for k, v in data.items() if k in known}
        extra = {k: v for k, v in data.items() if k not in known}
        settings = cls(**kwargs, extra=extra)
        settings.move_step = max(1, int(settings.move_step))
        return settings

    def save(self) -> None:
        data = asdict(self)
        data.update(data.pop("extra"))
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
