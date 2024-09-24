import logging
import threading
import time
import tkinter as tk
from tkinter import font
from tkinter import ttk

import markdown
import pyautogui
from pynput import keyboard
from tkhtmlview import HTMLLabel

from human_autoclicker.human_autoclicker import AutoClicker

# Configure logging to file and console
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("autoclicker.log", mode="a")
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


class AutoClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker")
        self.root.configure(bg="lightgray")

        self.auto_clicker = None
        self.thread = None
        self.hotkey = "f1"  # Default hotkey
        self.listener = None
        self.running = False
        self.prevent_mouse_movement_thread = None
        self.prevent_mouse_movement = False

        # Extract default values and parameter names from AutoClicker
        auto_clicker_defaults = AutoClicker.__init__.__defaults__
        auto_clicker_params = AutoClicker.__init__.__code__.co_varnames[
            1 : len(auto_clicker_defaults) + 1
        ]

        descriptions = {
            "click_interval": "Base interval between clicks in seconds",
            "click_interval_randomness": "Randomness added/subtracted to the base click interval in seconds",
            "click_interval_min": "Minimum interval between clicks in seconds",
            "click_fatigue_increase": "Amount by which click interval cumulatively increases due to fatigue in seconds",
            "hold_time": "Base duration to hold the click in seconds",
            "hold_time_randomness": "Randomness added to the base hold duration in seconds",
            "hold_time_min": "Minimum time the click is held in seconds",
            "hold_fatigue_increase": "Amount by which hold duration cumulatively increases due to fatigue in seconds",
            "fatigue_trigger_min_time": "Minimum interval for fatigue increase in seconds",
            "fatigue_trigger_max_time": "Maximum interval for fatigue increase in seconds",
            "short_break_duration": "Base duration for short breaks in seconds",
            "short_break_duration_randomness": "Randomness added to the base short break duration in seconds",
            "long_break_trigger_min_time": "Minimum interval between long breaks in seconds",
            "long_break_trigger_max_time": "Maximum interval between long breaks in seconds",
            "long_break_duration": "Base duration for long breaks in seconds",
            "long_break_duration_randomness": "Randomness added to the base long break duration in seconds",
            "max_runtime": "Maximum runtime for the script in seconds",
        }

        self.params = {
            param: (default, descriptions[param])
            for param, default in zip(auto_clicker_params, auto_clicker_defaults)
        }

        bold_font = font.Font(weight="bold")
        description_font = font.Font(slant="italic")

        self.entries = {}
        for idx, (param, (default, description)) in enumerate(self.params.items()):
            label = tk.Label(root, text=param, font=bold_font, background="lightgray")
            label.grid(row=idx, column=0, padx=10, pady=5, sticky=tk.W)
            desc_label = tk.Label(
                root,
                text=f"({description})",
                font=description_font,
                foreground="gray",
                background="lightgray",
            )
            desc_label.grid(row=idx, column=1, padx=10, pady=5, sticky=tk.W)
            entry = ttk.Entry(root, width=10)
            entry.insert(0, default)
            entry.grid(row=idx, column=2, padx=10, pady=5)
            self.entries[param] = entry

        # Hotkey entry field
        hotkey_idx = len(self.params)
        self.hotkey_label = tk.Label(
            root,
            text="Hotkey (Default: F1)",
            font=bold_font,
            foreground="darkred",
            background="lightgray",
        )
        self.hotkey_label.grid(row=hotkey_idx, column=0, padx=10, pady=5, sticky=tk.W)
        self.hotkey_entry = ttk.Entry(root, width=10)
        self.hotkey_entry.insert(0, "F1")
        self.hotkey_entry.grid(row=hotkey_idx, column=2, padx=10, pady=5)

        # Use tk.Frame for checkbox and button frames
        checkbox_frame = tk.Frame(root, background="lightgray")
        checkbox_frame.grid(row=hotkey_idx + 1, column=0, columnspan=3, pady=10)

        self.prevent_mouse_movement_var = tk.BooleanVar()
        self.prevent_mouse_movement_check = tk.Checkbutton(
            checkbox_frame,
            text="Lock Mouse Position",
            variable=self.prevent_mouse_movement_var,
            background="lightgray",
        )
        self.prevent_mouse_movement_check.grid(
            row=0, column=0, padx=10, pady=5, sticky=tk.W
        )

        disclaimer_label = tk.Label(
            checkbox_frame,
            text="(The mouse will move if you move it, but it will return to the original spot.)",
            font=description_font,
            foreground="gray",
            background="lightgray",
        )
        disclaimer_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

        button_frame = tk.Frame(root, background="lightgray")
        button_frame.grid(row=hotkey_idx + 2, column=0, columnspan=3, pady=10)

        button_font = font.Font(weight="bold")
        style = ttk.Style()
        style.configure("TButton", font=button_font)
        style.configure("Red.TButton", foreground="darkred", font=button_font)

        self.start_button = ttk.Button(
            button_frame, text="START", command=self.start_clicker, style="TButton"
        )
        self.start_button.grid(row=0, column=0, padx=10, pady=5, ipadx=20, ipady=10)

        self.stop_button = ttk.Button(
            button_frame, text="Stop", command=self.stop_clicker, style="TButton"
        )
        self.stop_button.grid(row=0, column=1, padx=10, pady=5, ipadx=20, ipady=10)

        self.update_hotkey_button = ttk.Button(
            button_frame,
            text="UPDATE HOTKEY",
            command=self.bind_hotkey,
            style="Red.TButton",
        )
        self.update_hotkey_button.grid(
            row=0, column=2, padx=10, pady=5, ipadx=20, ipady=10
        )

        self.show_logs_button = ttk.Button(
            button_frame, text="SHOW LOGS", command=self.show_logs, style="TButton"
        )
        self.show_logs_button.grid(row=0, column=3, padx=10, pady=5, ipadx=20, ipady=10)

        self.more_info_button = ttk.Button(
            button_frame, text="MORE INFO", command=self.show_more_info, style="TButton"
        )
        self.more_info_button.grid(row=0, column=4, padx=10, pady=5, ipadx=20, ipady=10)

        # Bind the default hotkey
        self.bind_hotkey()

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Bind the ESC key to stop the clicker
        self.root.bind("<Escape>", lambda event: self.stop_clicker())
        self.root.bind("<Control-w>", lambda event: self.on_closing())
        self.root.bind("<Alt-F4>", lambda event: self.on_closing())

        self.log_window = None
        self.log_text = None

        self.info_window = None
        self.info_text = None

    def bind_hotkey(self):
        new_hotkey = self.hotkey_entry.get().lower()
        if self.listener:
            self.listener.stop()
        try:
            self.listener = keyboard.GlobalHotKeys(
                {f"<{new_hotkey}>": self.toggle_clicker}
            )
            self.listener.start()
            logging.info(f"Hotkey set to: {self.hotkey}")
        except ValueError as e:
            logging.error(f"Invalid hotkey: {new_hotkey} - {e}")

    def toggle_clicker(self):
        if self.auto_clicker and self.auto_clicker.running:
            self.stop_clicker()
        else:
            self.start_clicker()

    def get_parameters(self):
        params = {}
        for param in self.params.keys():
            params[param] = float(self.entries[param].get())
        return params

    def start_clicker(self):
        if not self.running:
            params = self.get_parameters()
            self.auto_clicker = AutoClicker(**params)
            self.thread = threading.Thread(target=self.auto_clicker.start)
            self.thread.start()
            self.running = True
            logging.info("AutoClicker started")
            if self.prevent_mouse_movement_var.get():
                self.prevent_mouse_movement = True
                self.prevent_mouse_movement_thread = threading.Thread(
                    target=self.prevent_mouse_movement_function
                )
                self.prevent_mouse_movement_thread.start()

    def stop_clicker(self):
        if self.running and self.auto_clicker:
            self.auto_clicker.stop()
            self.thread.join()
            self.running = False
            logging.info("AutoClicker stopped")
            self.prevent_mouse_movement = False
            if self.prevent_mouse_movement_thread:
                self.prevent_mouse_movement_thread.join()

    def show_logs(self):
        if self.log_window is None or not self.log_window.winfo_exists():
            self.log_window = tk.Toplevel(self.root)
            self.log_window.title("Log Viewer")
            self.log_window.configure(bg="lightgray")
            self.log_text = tk.Text(self.log_window, wrap="word", bg="lightgray")
            self.log_text.pack(expand=1, fill="both")
            self.update_logs()

            # Bind the ESC key, Ctrl+W, and Alt+F4 to close the log window
            self.log_window.bind("<Escape>", lambda event: self.log_window.destroy())
            self.log_window.bind("<Control-w>", lambda event: self.log_window.destroy())
            self.log_window.bind("<Alt-F4>", lambda event: self.log_window.destroy())
        else:
            self.log_window.lift()

    def update_logs(self):
        with open("autoclicker.log") as log_file:
            self.log_text.delete("1.0", tk.END)
            self.log_text.insert(tk.END, log_file.read())
        self.log_text.after(1000, self.update_logs)

    def show_more_info(self):
        if self.info_window is None or not self.info_window.winfo_exists():
            self.info_window = tk.Toplevel(self.root)
            self.info_window.title("More Information")
            self.info_text = HTMLLabel(self.info_window, wrap="word")
            self.info_text.pack(expand=1, fill="both")

            # Read README.md and convert to HTML
            with open("README.md") as readme_file:
                readme_content = readme_file.read()
            html_content = markdown.markdown(readme_content)

            # Insert HTML content into the HTMLLabel widget
            self.info_text.set_html(html_content)

            # Bind the ESC key, Ctrl+W, and Alt+F4 to close the info window
            self.info_window.bind("<Escape>", lambda event: self.info_window.destroy())
            self.info_window.bind(
                "<Control-w>", lambda event: self.info_window.destroy()
            )
            self.info_window.bind("<Alt-F4>", lambda event: self.info_window.destroy())
        else:
            self.info_window.lift()

    def prevent_mouse_movement_function(self):
        initial_position = pyautogui.position()
        while self.prevent_mouse_movement:
            pyautogui.moveTo(initial_position)
            time.sleep(0.01)

    def on_closing(self):
        self.stop_clicker()  # Ensure the clicker stops
        self.root.destroy()  # Close the GUI


def main():
    root = tk.Tk()
    gui = AutoClickerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
