import win32gui
import win32con
import keyboard
import os
import tkinter as tk

# Global variables
default_move_pixels = 40  # Default value for moving pixels
resize_pixels = 1  # Fixed pixel increase for resizing

# Function to read move pixels from file
def get_move_pixels():
    if os.path.exists('move_pixels.txt'):
        with open('move_pixels.txt', 'r') as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return default_move_pixels
    return default_move_pixels

# Function to move the window up
def move_window_up(hwnd):
    move_pixels = get_move_pixels()
    rect = win32gui.GetWindowRect(hwnd)
    win32gui.SetWindowPos(
        hwnd, None, rect[0], rect[1] - move_pixels, rect[2] - rect[0], rect[3] - rect[1], win32con.SWP_NOZORDER
    )

# Function to move the window down
def move_window_down(hwnd):
    move_pixels = get_move_pixels()
    rect = win32gui.GetWindowRect(hwnd)
    win32gui.SetWindowPos(
        hwnd, None, rect[0], rect[1] + move_pixels, rect[2] - rect[0], rect[3] - rect[1], win32con.SWP_NOZORDER
    )

# Function to move the window left
def move_window_left(hwnd):
    move_pixels = get_move_pixels()
    rect = win32gui.GetWindowRect(hwnd)
    win32gui.SetWindowPos(
        hwnd, None, rect[0] - move_pixels, rect[1], rect[2] - rect[0], rect[3] - rect[1], win32con.SWP_NOZORDER
    )

# Function to move the window right
def move_window_right(hwnd):
    move_pixels = get_move_pixels()
    rect = win32gui.GetWindowRect(hwnd)
    win32gui.SetWindowPos(
        hwnd, None, rect[0] + move_pixels, rect[1], rect[2] - rect[0], rect[3] - rect[1], win32con.SWP_NOZORDER
    )

# Function to resize window
def resize_window(hwnd, left, right, top, bottom):
    move_pixels = get_move_pixels()
    rect = win32gui.GetWindowRect(hwnd)
    new_left = rect[0] - (left * move_pixels)
    new_top = rect[1] - (top * move_pixels)
    new_right = rect[2] + (right * move_pixels)
    new_bottom = rect[3] + (bottom * move_pixels)
    win32gui.SetWindowPos(
        hwnd, None, new_left, new_top,
        new_right - new_left, new_bottom - new_top, win32con.SWP_NOZORDER
    )

# Function to change opacity
def change_opacity(hwnd, increase=True):
    current_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    if not current_style & win32con.WS_EX_LAYERED:
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, current_style | win32con.WS_EX_LAYERED)
        new_opacity = 255  # Start with 100% opacity
    else:
        new_opacity = win32gui.GetLayeredWindowAttributes(hwnd)[1]

    new_opacity = min(255, new_opacity + 25) if increase else max(0, new_opacity - 25)
    win32gui.SetLayeredWindowAttributes(hwnd, 0, new_opacity, win32con.LWA_ALPHA)

# Function to display a message on the screen
def display_message(hwnd, message):
    title = win32gui.GetWindowText(hwnd)
    rect = win32gui.GetWindowRect(hwnd)

    overlay = tk.Tk()
    overlay.overrideredirect(True)
    overlay.attributes("-topmost", True)
    overlay.geometry(f"+{rect[0]}+{rect[1]}")

    label = tk.Label(overlay, text=f"{title}\n{message}", font=('Helvetica', 12), bg='yellow', fg='black')
    label.pack()

    overlay.update_idletasks()
    overlay.lift()
    overlay.after(2000, overlay.destroy)
    overlay.mainloop()

# Function to toggle always on top
def toggle_always_on_top(hwnd, always_on_top=True):
    win32gui.SetWindowPos(
        hwnd, win32con.HWND_TOPMOST if always_on_top else win32con.HWND_NOTOPMOST,
        0, 0, 0, 0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
    )
    display_message(hwnd, "Always on top turned on" if always_on_top else "Always on top turned off")

# Function to move window to another monitor
def move_to_next_monitor():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)
        current_monitor = win32api.MonitorFromWindow(hwnd)
        monitors = win32api.EnumDisplayMonitors()

        next_monitor = None
        for i, monitor in enumerate(monitors):
            if monitor[0] == current_monitor and i + 1 < len(monitors):
                next_monitor = monitors[i + 1]
                break

        if next_monitor:
            next_monitor_rect = next_monitor[2]
            new_x = next_monitor_rect[0] + (rect[0] - rect[2]) // 2
            new_y = next_monitor_rect[1] + (rect[1] - rect[3]) // 2
            win32gui.SetWindowPos(hwnd, None, new_x, new_y, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)

# Hotkey functions
def move_foreground_window_up():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        move_window_up(hwnd)

def move_foreground_window_down():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        move_window_down(hwnd)

def move_foreground_window_left():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        move_window_left(hwnd)

def move_foreground_window_right():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        move_window_right(hwnd)

def increase_left_side():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        resize_window(hwnd, 1, 0, 0, 0)

def increase_right_side():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        resize_window(hwnd, 0, 1, 0, 0)

def increase_bottom_side():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        resize_window(hwnd, 0, 0, 0, 1)

def increase_top_side():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        resize_window(hwnd, 0, 0, 1, 0)

def increase_opacity():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        change_opacity(hwnd, increase=True)

def decrease_opacity():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        change_opacity(hwnd, increase=False)

def set_always_on_top():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        toggle_always_on_top(hwnd, always_on_top=True)

def remove_always_on_top():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        toggle_always_on_top(hwnd, always_on_top=False)

# Registering hotkeys
def check_hotkeys():
    keyboard.add_hotkey('up', move_foreground_window_up)
    keyboard.add_hotkey('down', move_foreground_window_down)
    keyboard.add_hotkey('left', move_foreground_window_left)
    keyboard.add_hotkey('right', move_foreground_window_right)
    keyboard.add_hotkey('shift+left', increase_left_side)
    keyboard.add_hotkey('shift+right', increase_right_side)
    keyboard.add_hotkey('shift+down', increase_bottom_side)
    keyboard.add_hotkey('shift+up', increase_top_side)
    keyboard.add_hotkey('ctrl+up', increase_opacity)
    keyboard.add_hotkey('ctrl+down', decrease_opacity)
    keyboard.add_hotkey('ctrl+left', remove_always_on_top)
    keyboard.add_hotkey('ctrl+right', set_always_on_top)
    keyboard.add_hotkey('ctrl+shift+m', move_to_next_monitor)

def main():
    check_hotkeys()
    print("Hotkey listener started.")
    print("Use arrow keys to move the window and 'Shift + Arrow keys' to resize the window.")
    print("Use 'Ctrl + Up/Down' to change opacity, 'Ctrl + Left/Right' to toggle always on top.")
    print("Use 'Ctrl + Shift + M' to move the window to the next monitor.")
    # Prevent the script from exiting
    keyboard.wait()

if __name__ == "__main__":
    main()
