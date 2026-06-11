"""Global hotkey engine.

Registers the system-wide hotkeys with the `keyboard` library and routes
them to the win32 window actions. The hotkey map is intentionally identical
to the original tool:

    Arrow keys            move the focused window
    Shift + Arrow keys    grow the window in that direction
    Ctrl  + Up / Down     increase / decrease opacity
    Ctrl  + Right         set always on top
    Ctrl  + Left          remove always on top
    Ctrl  + Shift + M     move window to the next monitor
"""

from __future__ import annotations

import sys
import threading
from typing import Callable

from . import window_actions
from .config import Settings

WINDOWS = sys.platform == "win32"

if WINDOWS:
    import keyboard

# (hotkey, description) - single source of truth, also rendered on the
# GUI's Hotkeys page.
HOTKEY_REFERENCE = [
    ("↑ ↓ ← →", "Move the focused window"),
    ("Shift + ↑ ↓ ← →", "Resize the window (grow that edge)"),
    ("Ctrl + ↑", "Increase opacity"),
    ("Ctrl + ↓", "Decrease opacity"),
    ("Ctrl + →", "Set always on top"),
    ("Ctrl + ←", "Remove always on top"),
    ("Ctrl + Shift + M", "Move window to next monitor"),
]


class HotkeyEngine:
    """Owns the global hotkey registrations.

    `on_event` is called (from the keyboard library's listener thread) with
    a status string after each action, so the GUI can show what happened.
    """

    def __init__(self, settings: Settings, on_event: Callable[[str], None]):
        self.settings = settings
        self.on_event = on_event
        self._lock = threading.Lock()
        self._handles: list = []

    @property
    def running(self) -> bool:
        return bool(self._handles)

    def start(self) -> None:
        if not WINDOWS:
            self.on_event("Hotkeys require Windows - running in preview mode")
            return
        with self._lock:
            if self._handles:
                return
            step = lambda: self.settings.move_step  # noqa: E731
            ostep = lambda: self.settings.opacity_step  # noqa: E731
            bindings = {
                "up": lambda: window_actions.move(0, -1, step()),
                "down": lambda: window_actions.move(0, 1, step()),
                "left": lambda: window_actions.move(-1, 0, step()),
                "right": lambda: window_actions.move(1, 0, step()),
                "shift+up": lambda: window_actions.resize(0, 1, 0, 0, step()),
                "shift+down": lambda: window_actions.resize(0, 0, 0, 1, step()),
                "shift+left": lambda: window_actions.resize(1, 0, 0, 0, step()),
                "shift+right": lambda: window_actions.resize(0, 0, 1, 0, step()),
                "ctrl+up": lambda: window_actions.change_opacity(True, ostep()),
                "ctrl+down": lambda: window_actions.change_opacity(False, ostep()),
                "ctrl+right": lambda: window_actions.set_always_on_top(True),
                "ctrl+left": lambda: window_actions.set_always_on_top(False),
                "ctrl+shift+m": window_actions.move_to_next_monitor,
            }
            for combo, action in bindings.items():
                self._handles.append(
                    keyboard.add_hotkey(combo, self._wrap(action), suppress=False)
                )
        self.on_event("Hotkeys enabled")

    def stop(self) -> None:
        with self._lock:
            if not self._handles:
                return
            for handle in self._handles:
                try:
                    keyboard.remove_hotkey(handle)
                except (KeyError, ValueError):
                    pass
            self._handles.clear()
        self.on_event("Hotkeys disabled")

    def _wrap(self, action: Callable[[], str]) -> Callable[[], None]:
        def run() -> None:
            try:
                message = action()
            except Exception as exc:  # never let a hotkey kill the listener
                message = f"Error: {exc}"
            if message:
                self.on_event(message)

        return run
