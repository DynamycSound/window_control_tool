"""Modern CustomTkinter GUI for the Window Control Tool.

Layout: a sidebar with four pages (Home, Hotkeys, Settings, About). Help
and theme options - previously separate popup windows - are regular pages
now, so everything lives in one window.
"""

from __future__ import annotations

import sys
import webbrowser
from datetime import datetime

import customtkinter as ctk

from . import __version__
from .config import DEFAULT_MOVE_STEP, Settings
from .hotkeys import HOTKEY_REFERENCE, WINDOWS, HotkeyEngine

REPO_URL = "https://github.com/DynamycSound/window_control_tool"

ACCENT = "#3B8ED0"
GREEN = "#2FA572"
RED = "#D04B3B"


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.settings = Settings.load()
        ctk.set_appearance_mode(self.settings.appearance_mode)

        self.engine = HotkeyEngine(self.settings, self._on_engine_event)

        self.title("Window Control Tool")
        self.geometry("760x520")
        self.minsize(640, 460)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._pages: dict[str, ctk.CTkFrame] = {
            "home": self._build_home_page(),
            "hotkeys": self._build_hotkeys_page(),
            "settings": self._build_settings_page(),
            "about": self._build_about_page(),
        }
        self._show_page("home")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        if not WINDOWS:
            self._log("Preview mode: hotkeys only work on Windows.")
        if self.settings.start_hotkeys_on_launch and WINDOWS:
            self._toggle_hotkeys_from_switch(force_on=True)

    # ------------------------------------------------------------- sidebar

    def _build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(self, width=180, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(
            sidebar, text="Window\nControl Tool",
            font=ctk.CTkFont(size=20, weight="bold"), justify="left",
        ).grid(row=0, column=0, padx=20, pady=(24, 4), sticky="w")
        ctk.CTkLabel(
            sidebar, text=f"v{__version__}", text_color="gray",
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        for row, (key, label) in enumerate(
            [("home", "  Home"), ("hotkeys", "  Hotkeys"),
             ("settings", "  Settings"), ("about", "  About")],
            start=2,
        ):
            button = ctk.CTkButton(
                sidebar, text=label, anchor="w", height=40,
                fg_color="transparent", text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray25"),
                command=lambda k=key: self._show_page(k),
            )
            button.grid(row=row, column=0, padx=12, pady=2, sticky="ew")
            self._nav_buttons[key] = button

        self.sidebar_status = ctk.CTkLabel(
            sidebar, text="●  Hotkeys off", text_color="gray",
            font=ctk.CTkFont(size=13),
        )
        self.sidebar_status.grid(row=7, column=0, padx=20, pady=16, sticky="w")

    def _show_page(self, key: str) -> None:
        for name, page in self._pages.items():
            page.grid_forget()
        self._pages[key].grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        for name, button in self._nav_buttons.items():
            button.configure(
                fg_color=("gray75", "gray28") if name == key else "transparent"
            )

    # ---------------------------------------------------------------- home

    def _build_home_page(self) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(3, weight=1)

        # Power card
        card = ctk.CTkFrame(page)
        card.grid(row=0, column=0, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            card, text="Global hotkeys",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(14, 0), sticky="w")
        self.status_label = ctk.CTkLabel(
            card, text="Off - flip the switch to start controlling windows",
            text_color="gray",
        )
        self.status_label.grid(row=1, column=0, padx=16, pady=(0, 14), sticky="w")
        self.power_switch = ctk.CTkSwitch(
            card, text="", width=80, switch_height=28, switch_width=56,
            progress_color=GREEN, command=self._toggle_hotkeys_from_switch,
        )
        self.power_switch.grid(row=0, column=1, rowspan=2, padx=16)

        # Move step card
        step_card = ctk.CTkFrame(page)
        step_card.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        step_card.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            step_card, text="Move / resize step",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, padx=16, pady=(12, 2), sticky="w")
        ctk.CTkLabel(
            step_card, text="How many pixels each hotkey press moves or resizes "
            "the window.", text_color="gray",
        ).grid(row=1, column=0, columnspan=3, padx=16, sticky="w")

        self.step_slider = ctk.CTkSlider(
            step_card, from_=1, to=200, number_of_steps=199,
            command=self._on_step_slider,
        )
        self.step_slider.set(self.settings.move_step)
        self.step_slider.grid(row=2, column=0, columnspan=2, padx=16,
                              pady=12, sticky="ew")

        entry_row = ctk.CTkFrame(step_card, fg_color="transparent")
        entry_row.grid(row=2, column=2, padx=(0, 16), pady=12)
        self.step_entry = ctk.CTkEntry(entry_row, width=64, justify="center")
        self.step_entry.insert(0, str(self.settings.move_step))
        self.step_entry.bind("<Return>", lambda _e: self._on_step_entry())
        self.step_entry.bind("<FocusOut>", lambda _e: self._on_step_entry())
        self.step_entry.pack(side="left", padx=(0, 6))
        ctk.CTkLabel(entry_row, text="px", text_color="gray").pack(side="left")
        ctk.CTkButton(
            entry_row, text="Reset", width=56,
            fg_color="transparent", border_width=1,
            text_color=("gray10", "gray90"),
            command=lambda: self._set_step(DEFAULT_MOVE_STEP),
        ).pack(side="left", padx=(10, 0))

        # Activity log
        ctk.CTkLabel(
            page, text="Activity", font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=2, column=0, sticky="w", pady=(14, 4))
        self.log_box = ctk.CTkTextbox(page, state="disabled",
                                      font=ctk.CTkFont(size=12))
        self.log_box.grid(row=3, column=0, sticky="nsew")
        return page

    # ------------------------------------------------------------- hotkeys

    def _build_hotkeys_page(self) -> ctk.CTkFrame:
        page = ctk.CTkScrollableFrame(self, fg_color="transparent")
        page.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            page, text="Hotkeys", font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))
        ctk.CTkLabel(
            page, text="These work system-wide while hotkeys are enabled. "
            "They always act on the window that currently has focus.",
            text_color="gray", wraplength=480, justify="left",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 14))

        for row, (combo, description) in enumerate(HOTKEY_REFERENCE, start=2):
            chip = ctk.CTkLabel(
                page, text=f"  {combo}  ",
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=("gray80", "gray25"), corner_radius=6,
            )
            chip.grid(row=row, column=0, sticky="w", pady=5)
            ctk.CTkLabel(page, text=description, anchor="w").grid(
                row=row, column=1, sticky="w", padx=14, pady=5
            )

        tip = ctk.CTkFrame(page)
        tip.grid(row=len(HOTKEY_REFERENCE) + 2, column=0, columnspan=2,
                 sticky="ew", pady=(18, 0))
        ctk.CTkLabel(
            tip, text="Tip", font=ctk.CTkFont(size=13, weight="bold"),
            text_color=ACCENT,
        ).pack(anchor="w", padx=14, pady=(10, 0))
        ctk.CTkLabel(
            tip, text="The arrow keys are captured globally while hotkeys are "
            "on, so turn the switch off when you need normal arrow-key "
            "behaviour (e.g. while typing in a document).",
            text_color="gray", wraplength=460, justify="left",
        ).pack(anchor="w", padx=14, pady=(2, 12))
        return page

    # ------------------------------------------------------------ settings

    def _build_settings_page(self) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            page, text="Settings", font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 14))

        card = ctk.CTkFrame(page)
        card.grid(row=1, column=0, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Appearance", anchor="w").grid(
            row=0, column=0, padx=16, pady=12, sticky="w")
        self.appearance_menu = ctk.CTkOptionMenu(
            card, values=["Dark", "Light", "System"],
            command=self._on_appearance_change, width=130,
        )
        self.appearance_menu.set(self.settings.appearance_mode.capitalize())
        self.appearance_menu.grid(row=0, column=1, padx=16, pady=12)

        ctk.CTkLabel(card, text="Opacity change per press", anchor="w").grid(
            row=1, column=0, padx=16, pady=12, sticky="w")
        self.opacity_menu = ctk.CTkOptionMenu(
            card, values=["10", "25", "50"], width=130,
            command=self._on_opacity_step_change,
        )
        self.opacity_menu.set(str(self.settings.opacity_step))
        self.opacity_menu.grid(row=1, column=1, padx=16, pady=12)

        ctk.CTkLabel(card, text="Enable hotkeys when the app starts",
                     anchor="w").grid(row=2, column=0, padx=16, pady=12,
                                      sticky="w")
        self.autostart_switch = ctk.CTkSwitch(
            card, text="", command=self._on_autostart_change,
            progress_color=GREEN,
        )
        if self.settings.start_hotkeys_on_launch:
            self.autostart_switch.select()
        self.autostart_switch.grid(row=2, column=1, padx=16, pady=12)

        ctk.CTkLabel(
            page, text="Settings are saved automatically.",
            text_color="gray", font=ctk.CTkFont(size=12),
        ).grid(row=2, column=0, sticky="w", pady=10)
        return page

    # --------------------------------------------------------------- about

    def _build_about_page(self) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(
            page, text="About", font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w", pady=(0, 14))

        card = ctk.CTkFrame(page)
        card.pack(fill="x")
        ctk.CTkLabel(
            card, text="Window Control Tool",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(14, 0))
        ctk.CTkLabel(
            card,
            text=(
                f"Version {__version__}\n"
                "Move, resize and restyle any window with global hotkeys.\n\n"
                "Free and open source under the MIT License - you may use, "
                "modify and redistribute it freely."
            ),
            text_color="gray", justify="left", wraplength=460,
        ).pack(anchor="w", padx=16, pady=(4, 14))

        buttons = ctk.CTkFrame(page, fg_color="transparent")
        buttons.pack(fill="x", pady=12)
        ctk.CTkButton(
            buttons, text="GitHub repository",
            command=lambda: webbrowser.open(REPO_URL),
        ).pack(side="left")
        ctk.CTkButton(
            buttons, text="Report an issue", fg_color="transparent",
            border_width=1, text_color=("gray10", "gray90"),
            command=lambda: webbrowser.open(f"{REPO_URL}/issues/new/choose"),
        ).pack(side="left", padx=10)
        return page

    # ------------------------------------------------------------ handlers

    def _toggle_hotkeys_from_switch(self, force_on: bool = False) -> None:
        if force_on:
            self.power_switch.select()
        if self.power_switch.get():
            self.engine.start()
        else:
            self.engine.stop()
        self._refresh_status()

    def _refresh_status(self) -> None:
        if self.engine.running:
            self.status_label.configure(
                text="On - hotkeys are active system-wide", text_color=GREEN)
            self.sidebar_status.configure(text="●  Hotkeys on",
                                          text_color=GREEN)
        else:
            self.status_label.configure(
                text="Off - flip the switch to start controlling windows",
                text_color="gray")
            self.sidebar_status.configure(text="●  Hotkeys off",
                                          text_color="gray")
            self.power_switch.deselect()

    def _set_step(self, value: int) -> None:
        value = max(1, min(999, value))
        self.settings.move_step = value
        self.step_slider.set(min(value, 200))
        self.step_entry.delete(0, "end")
        self.step_entry.insert(0, str(value))
        self.settings.save()

    def _on_step_slider(self, value: float) -> None:
        self._set_step(int(value))

    def _on_step_entry(self) -> None:
        try:
            value = int(self.step_entry.get())
        except ValueError:
            self._set_step(self.settings.move_step)
            self._log("Invalid step value - keeping previous setting.")
            return
        self._set_step(value)

    def _on_appearance_change(self, choice: str) -> None:
        self.settings.appearance_mode = choice.lower()
        ctk.set_appearance_mode(self.settings.appearance_mode)
        self.settings.save()

    def _on_opacity_step_change(self, choice: str) -> None:
        self.settings.opacity_step = int(choice)
        self.settings.save()

    def _on_autostart_change(self) -> None:
        self.settings.start_hotkeys_on_launch = bool(self.autostart_switch.get())
        self.settings.save()

    def _on_engine_event(self, message: str) -> None:
        # Called from the keyboard listener thread - marshal to the UI thread.
        self.after(0, self._log, message)

    def _log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{timestamp}] {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        self._refresh_status()

    def _on_close(self) -> None:
        self.engine.stop()
        self.destroy()


def run() -> int:
    if sys.platform != "win32":
        print("Note: Window Control Tool targets Windows; "
              "the GUI will open in preview mode without hotkeys.")
    app = App()
    app.mainloop()
    return 0
