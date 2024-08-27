import tkinter as tk
from tkinter import ttk, colorchooser
from PIL import Image, ImageTk
import subprocess
import threading
import os
import json

# Global variables
background_process = None
move_pixels = 40  # Default value for moving pixels
settings_file = 'settings.json'
default_settings = {
    'theme': 'dark',
    'background_color': '#000000',
    'font_color': '#00FF00'
}

def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings = json.load(f)
            # Ensure default settings are present
            for key, value in default_settings.items():
                settings.setdefault(key, value)
            return settings
    return default_settings

def save_settings(settings):
    with open(settings_file, 'w') as f:
        json.dump(settings, f)

def apply_settings(settings):
    global background_color, font_color
    background_color = settings['background_color']
    font_color = settings['font_color']
    root.configure(bg=background_color)
    style.configure('TButton', background=background_color, foreground=font_color)
    style.configure('TLabel', background=background_color, foreground=font_color)
    style.configure("Custom.TEntry", fieldbackground=background_color, foreground=font_color, insertcolor=font_color)
    
    move_pixels_entry.configure(style="Custom.TEntry")
    help_button.configure(bg=background_color, fg=font_color)
    theme_button.configure(bg=background_color, fg=font_color)
    confirm_button.configure(bg=background_color, fg=font_color)
    toggle_button.configure(bg=background_color)
    
    for button in [decrease_button_1, decrease_button_5, increase_button_1, increase_button_5]:
        button.configure(bg=background_color, fg=font_color)
    
    for label in [label_move_pixels, label_default, output_label, console_output_label, author_label]:
        label.configure(background=background_color, foreground=font_color)
    
    frame.configure(bg=background_color)

def update_theme_window(window):
    for widget in window.winfo_children():
        try:
            widget.configure(bg=settings['background_color'], fg=settings['font_color'])
        except tk.TclError:
            pass

def start_or_restart_script():
    global background_process

    if background_process and background_process.poll() is None:
        background_process.terminate()

    try:
        global move_pixels
        move_pixels = int(move_pixels_entry.get())
    except ValueError:
        console_output.set("Invalid input for pixels. Default: 40")
        move_pixels = 40
        move_pixels_entry.delete(0, tk.END)
        move_pixels_entry.insert(0, move_pixels)
        return

    with open('move_pixels.txt', 'w') as f:
        f.write(str(move_pixels))

    background_process = subprocess.Popen(['python', 'togglewindows.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    threading.Thread(target=read_output, daemon=True).start()
    console_output.set("")
    update_status_indicator()

def stop_script():
    global background_process
    if background_process and background_process.poll() is None:
        background_process.terminate()
    console_output.set("Script stopped")
    update_status_indicator()

def update_move_pixels():
    global move_pixels
    try:
        move_pixels = int(move_pixels_entry.get())
        with open('move_pixels.txt', 'w') as f:
            f.write(str(move_pixels))
        console_output.set(f"Move pixels updated to {move_pixels}")
    except ValueError:
        console_output.set("Invalid input for pixels. Please enter a valid number.")

def decrease_move_pixels(by_value=1):
    current_value = int(move_pixels_entry.get())
    new_value = max(current_value - by_value, 0)
    move_pixels_entry.delete(0, tk.END)
    move_pixels_entry.insert(0, new_value)

def increase_move_pixels(by_value=1):
    current_value = int(move_pixels_entry.get())
    new_value = current_value + by_value
    move_pixels_entry.delete(0, tk.END)
    move_pixels_entry.insert(0, new_value)

def update_status_indicator():
    if "Script stopped" in console_output.get() or "Press power button to start the script" in console_output.get():
        toggle_button.config(image=off_image)
    else:
        toggle_button.config(image=on_image)

def toggle_script():
    if "Script stopped" in console_output.get() or "Press power button to start the script" in console_output.get():
        start_or_restart_script()
    else:
        stop_script()

def read_output():
    global background_process
    while background_process and background_process.poll() is None:
        output_line = background_process.stdout.readline()
        if output_line:
            console_output.set(output_line.strip())
            update_status_indicator()

def show_help():
    help_window = tk.Toplevel(root)
    help_window.title("Help")
    help_window.geometry("300x400")
    help_window.configure(bg=background_color)
    help_text = (
        "Window Control Tool Help\n\n"
        "Hotkeys:\n"
        "- Arrow keys: Move window\n"
        "- Shift + Arrow keys: Resize window\n"
        "- Ctrl + Up: Increase opacity\n"
        "- Ctrl + Down: Decrease opacity\n"
        "- Ctrl + Left: Remove always on top\n"
        "- Ctrl + Right: Set always on top\n\n"
        "Buttons:\n"
        "- Start: Start the script\n"
        "- Stop: Stop the script\n"
        "- Confirm: Update move pixels value\n"
    )
    ttk.Label(help_window, text=help_text, background=background_color, foreground=font_color, justify='left', wraplength=280).pack(pady=10, padx=10)
    update_theme_window(help_window)

def show_theme_settings():
    theme_window = tk.Toplevel(root)
    theme_window.title("Theme Settings")
    theme_window.geometry("300x400")
    theme_window.configure(bg=background_color)

    def apply_theme(theme):
        if theme == 'dark':
            settings.update({'theme': 'dark', 'background_color': '#000000', 'font_color': '#00FF00'})
        elif theme == 'light':
            settings.update({'theme': 'light', 'background_color': '#FFFFFF', 'font_color': '#000000'})
        apply_settings(settings)
        save_settings(settings)
        theme_window.configure(bg=settings['background_color'])
        update_theme_window(theme_window)
        for window in root.winfo_children():
            if isinstance(window, tk.Toplevel):
                update_theme_window(window)

    def set_custom_color(setting_key):
        current_color = settings[setting_key]
        color = colorchooser.askcolor(initialcolor=current_color, title=f"Choose {setting_key.replace('_', ' ')}")[1]
        if color:
            settings[setting_key] = color
            apply_settings(settings)
            save_settings(settings)
            theme_window.configure(bg=settings['background_color'])
            update_theme_window(theme_window)
            for window in root.winfo_children():
                if isinstance(window, tk.Toplevel):
                    update_theme_window(window)

    for widget in theme_window.winfo_children():
        widget.destroy()
    
    ttk.Button(theme_window, text="Dark Mode", command=lambda: apply_theme('dark')).pack(pady=10)
    ttk.Button(theme_window, text="Light Mode", command=lambda: apply_theme('light')).pack(pady=10)
    
    custom_mode_button = ttk.Button(theme_window, text="Custom Mode", command=lambda: show_custom_mode_options(theme_window, update_theme_window))
    custom_mode_button.pack(pady=10)
    
    update_theme_window(theme_window)

def show_custom_mode_options(theme_window, update_theme_window):
    def set_custom_color(setting_key):
        current_color = settings[setting_key]
        color = colorchooser.askcolor(initialcolor=current_color, title=f"Choose {setting_key.replace('_', ' ')}")[1]
        if color:
            settings[setting_key] = color
            apply_settings(settings)
            save_settings(settings)
            theme_window.configure(bg=settings['background_color'])
            update_theme_window(theme_window)
            for window in root.winfo_children():
                if isinstance(window, tk.Toplevel):
                    update_theme_window(window)

    for widget in theme_window.winfo_children():
        if widget.cget("text") in ["Background Color", "Font Color"]:
            widget.destroy()
    ttk.Button(theme_window, text="Background Color", command=lambda: set_custom_color('background_color')).pack(pady=5)
    ttk.Button(theme_window, text="Font Color", command=lambda: set_custom_color('font_color')).pack(pady=5)

def main():
    global move_pixels_entry, background_process, console_output, toggle_button, root, on_image, off_image, background_color, font_color, style, help_button, theme_button, confirm_button, output_label, console_output_label, author_label, decrease_button_1, decrease_button_5, increase_button_1, increase_button_5, label_move_pixels, label_default, settings, frame

    settings = load_settings()
    background_color = settings['background_color']
    font_color = settings['font_color']

    # Read initial move_pixels value from file
    if os.path.exists('move_pixels.txt'):
        with open('move_pixels.txt', 'r') as f:
            try:
                move_pixels = int(f.read().strip())
            except ValueError:
                move_pixels = 40

    root = tk.Tk()
    root.title("Window Control Tool")
    root.geometry("300x500")
    root.pack_propagate(False)

    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('TButton', font=('Helvetica', 14), padding=5, background=background_color, foreground=font_color)
    style.configure('TLabel', font=('Helvetica', 14), padding=5, background=background_color, foreground=font_color)
    style.configure('TEntry', font=('Helvetica', 14), padding=5)
    style.configure("Custom.TEntry",
                    fieldbackground=background_color,
                    foreground=font_color,
                    insertcolor=font_color)

    root.configure(bg=background_color)

    label_move_pixels = ttk.Label(root, text="Enter move pixels:", background=background_color, foreground=font_color)
    label_move_pixels.pack(pady=5)

    frame = tk.Frame(root, bg=background_color)
    frame.pack(pady=5)

    decrease_button_1 = tk.Button(frame, text="-1", width=3, command=lambda: decrease_move_pixels(1), bg=background_color, fg=font_color)
    decrease_button_1.grid(row=0, column=0, padx=2)

    decrease_button_5 = tk.Button(frame, text="-5", width=3, command=lambda: decrease_move_pixels(5), bg=background_color, fg=font_color)
    decrease_button_5.grid(row=0, column=1, padx=2)

    move_pixels_entry = ttk.Entry(frame, width=10, style="Custom.TEntry")
    move_pixels_entry.insert(0, move_pixels)
    move_pixels_entry.grid(row=0, column=2)

    increase_button_1 = tk.Button(frame, text="+1", width=3, command=lambda: increase_move_pixels(1), bg=background_color, fg=font_color)
    increase_button_1.grid(row=0, column=3, padx=2)

    increase_button_5 = tk.Button(frame, text="+5", width=3, command=lambda: increase_move_pixels(5), bg=background_color, fg=font_color)
    increase_button_5.grid(row=0, column=4, padx=2)

    confirm_button = tk.Button(root, text="Confirm", command=update_move_pixels, bg=background_color, fg=font_color)
    confirm_button.pack(pady=5)

    label_default = ttk.Label(root, text="Default: 40", background=background_color, foreground=font_color)
    label_default.pack(pady=5)

    # Load images for toggle button
    on_image = ImageTk.PhotoImage(Image.open("on.png").resize((40, 40)))
    off_image = ImageTk.PhotoImage(Image.open("off.png").resize((40, 40)))

    # Create toggle button with image
    toggle_button = tk.Button(root, image=off_image, command=toggle_script, bg=background_color)
    toggle_button.pack(pady=5)

    output_text = tk.StringVar()
    output_text.set("Output:")
    output_label = ttk.Label(root, textvariable=output_text, background=background_color, foreground=font_color)
    output_label.pack(pady=5)

    # Console output area
    console_output = tk.StringVar()
    console_output_label = ttk.Label(root, textvariable=console_output, background=background_color, foreground=font_color, anchor='center', justify='center', wraplength=250)
    console_output_label.pack(pady=5, fill='x', padx=5)

    # Help button
    help_button = tk.Button(root, text="How to use this?", command=show_help, bg=background_color, fg=font_color)
    help_button.pack(pady=5)

    # Theme settings button
    theme_button = tk.Button(root, text="Theme Settings", command=show_theme_settings, bg=background_color, fg=font_color)
    theme_button.pack(pady=5)

    # Author label
    author_label = ttk.Label(root, text="Made by Stefan M.", background=background_color, foreground=font_color, anchor='center', justify='center')
    author_label.place(relx=0.5, rely=1.0, anchor='s', y=-5)

    # Initialize console with initial instruction
    console_output.set("Press power button to start the script")

    def on_closing():
        stop_script()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    apply_settings(settings)
    root.mainloop()

if __name__ == "__main__":
    main()
