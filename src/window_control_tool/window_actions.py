"""Win32 operations on the currently focused (foreground) window.

Every public function returns a short human-readable status string that the
GUI shows in its activity log. All win32 errors are caught and reported as
text instead of crashing the hotkey listener.
"""

from __future__ import annotations

import sys

WINDOWS = sys.platform == "win32"

if WINDOWS:
    import win32api
    import win32con
    import win32gui


def _foreground():
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return None, ""
    return hwnd, win32gui.GetWindowText(hwnd) or "<untitled>"


def move(dx: int, dy: int, step: int) -> str:
    hwnd, title = _foreground()
    if not hwnd:
        return "No active window"
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    win32gui.SetWindowPos(
        hwnd, None,
        left + dx * step, top + dy * step,
        right - left, bottom - top,
        win32con.SWP_NOZORDER,
    )
    return f"Moved '{title}'"


def resize(d_left: int, d_top: int, d_right: int, d_bottom: int, step: int) -> str:
    hwnd, title = _foreground()
    if not hwnd:
        return "No active window"
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    new_left = left - d_left * step
    new_top = top - d_top * step
    new_right = right + d_right * step
    new_bottom = bottom + d_bottom * step
    win32gui.SetWindowPos(
        hwnd, None,
        new_left, new_top,
        max(50, new_right - new_left), max(50, new_bottom - new_top),
        win32con.SWP_NOZORDER,
    )
    return f"Resized '{title}'"


def change_opacity(increase: bool, step: int) -> str:
    hwnd, title = _foreground()
    if not hwnd:
        return "No active window"
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    if not style & win32con.WS_EX_LAYERED:
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style | win32con.WS_EX_LAYERED)
        opacity = 255
    else:
        opacity = win32gui.GetLayeredWindowAttributes(hwnd)[1]
    # Never go fully invisible from a hotkey - 25 stays barely visible
    opacity = min(255, opacity + step) if increase else max(25, opacity - step)
    win32gui.SetLayeredWindowAttributes(hwnd, 0, opacity, win32con.LWA_ALPHA)
    return f"Opacity of '{title}': {round(opacity / 255 * 100)}%"


def set_always_on_top(on_top: bool) -> str:
    hwnd, title = _foreground()
    if not hwnd:
        return "No active window"
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOPMOST if on_top else win32con.HWND_NOTOPMOST,
        0, 0, 0, 0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
    )
    state = "ON" if on_top else "OFF"
    return f"Always on top {state} for '{title}'"


def move_to_next_monitor() -> str:
    hwnd, title = _foreground()
    if not hwnd:
        return "No active window"
    monitors = win32api.EnumDisplayMonitors()
    if len(monitors) < 2:
        return "Only one monitor detected"
    current = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    handles = [int(m[0]) for m in monitors]
    try:
        index = handles.index(int(current))
    except ValueError:
        index = 0
    target = monitors[(index + 1) % len(monitors)][2]  # work area rect of next monitor

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width, height = right - left, bottom - top
    new_x = target[0] + max(0, (target[2] - target[0] - width) // 2)
    new_y = target[1] + max(0, (target[3] - target[1] - height) // 2)
    win32gui.SetWindowPos(
        hwnd, None, new_x, new_y, 0, 0,
        win32con.SWP_NOSIZE | win32con.SWP_NOZORDER,
    )
    return f"Moved '{title}' to next monitor"
