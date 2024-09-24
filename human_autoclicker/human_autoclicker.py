import logging
import random
import time
import tkinter as tk

import pyautogui

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    filename="autoclicker.log",
    filemode="w",
)


class AutoClicker:
    def __init__(
        self,
        click_interval=0.34,  # Base time interval between clicks
        click_interval_randomness=0.21,  # Randomness added/subtracted to the base click interval
        click_interval_min=0.06,  # Minimum interval to ensure between clicks
        click_fatigue_increase=0.02,  # Amount by which click interval cumulitative increases due to fatigue
        hold_time=0.21,  # Base duration to hold the click
        hold_time_randomness=0.14,  # Randomness added to the base hold duration
        hold_time_min=0.02,  # Minimum time the click is held
        hold_fatigue_increase=0.01,  # Amount by which hold duration increases cumulitative due to fatigue
        fatigue_trigger_min_time=118,  # Minimum interval of time until fatigue is triggered
        fatigue_trigger_max_time=217,  # Maximum interval of time until fatigue is triggered
        short_break_duration=21,  # Base duration for short breaks
        short_break_duration_randomness=13,  # Randomness added/subtracted to the base short break duration
        long_break_trigger_min_time=589,  # Minimum interval of time until long break is triggered
        long_break_trigger_max_time=1277,  # Maximum interval of time until long break is triggered
        long_break_duration=139,  # Base duration for long breaks
        long_break_duration_randomness=77,  # Randomness added to the base long break duration
        max_runtime=7149,  # Maximum runtime for the script
    ):
        self.click_interval = click_interval
        self.click_interval_randomness = click_interval_randomness
        self.click_interval_min = click_interval_min
        self.hold_time = hold_time
        self.hold_time_randomness = hold_time_randomness
        self.hold_fatigue_increase = hold_fatigue_increase
        self.hold_time_min = hold_time_min
        self.fatigue_trigger_min_time = fatigue_trigger_min_time
        self.fatigue_trigger_max_time = fatigue_trigger_max_time
        self.click_fatigue_increase = click_fatigue_increase
        self.short_break_duration = short_break_duration
        self.short_break_duration_randomness = short_break_duration_randomness
        self.long_break_trigger_min_time = long_break_trigger_min_time
        self.long_break_trigger_max_time = long_break_trigger_max_time
        self.long_break_duration = long_break_duration
        self.long_break_duration_randomness = long_break_duration_randomness
        self.max_runtime = max_runtime
        self.running = False  # This will control the running state of the clicker
        self.next_fatigue_time = time.time() + random.uniform(
            self.fatigue_trigger_min_time, self.fatigue_trigger_max_time
        )
        self.next_long_break_time = time.time() + random.uniform(
            self.long_break_trigger_min_time, self.long_break_trigger_max_time
        )
        self.click_fatigue = 0
        self.hold_fatigue = 0
        self.accumulated_click_fatigue_delay = 0  # To accumulate click fatigue delay
        self.accumulated_hold_fatigue_delay = 0  # To accumulate hold fatigue delay
        self.last_short_break_time = start_time = (
            time.time()
        )  # Track the last short break time
        self.last_long_break_time = start_time  # Track the last long break time

        # Attributes for preventing mouse movement
        self.prevent_mouse_movement = False
        self.prevent_mouse_movement_thread = None

    def randomize_uniform(self, base, randomness):
        return base + random.uniform(-randomness, randomness)

    def randomize_normal(self, base, randomness):
        return base + random.gauss(0, randomness)

    def update_fatigue(self):
        current_time = time.time()
        if current_time >= self.next_fatigue_time:
            self.click_fatigue += random.uniform(0.005, self.click_fatigue_increase)
            self.hold_fatigue += random.uniform(0.005, self.hold_fatigue_increase)
            self.accumulated_click_fatigue_delay += self.randomize_normal(
                self.click_interval, self.click_interval_randomness
            )
            self.accumulated_hold_fatigue_delay += self.randomize_normal(
                self.hold_time, self.hold_time_randomness
            )
            self.next_fatigue_time = current_time + random.uniform(
                self.fatigue_trigger_min_time, self.fatigue_trigger_max_time
            )
            logging.info(
                f"Fatigue updated: click_fatigue={self.click_fatigue}, hold_fatigue={self.hold_fatigue}"
            )

    def reset_fatigue(self):
        self.click_fatigue = 0
        self.hold_fatigue = 0
        self.accumulated_click_fatigue_delay = (
            0  # Reset accumulated click fatigue delay
        )
        self.accumulated_hold_fatigue_delay = 0  # Reset accumulated hold fatigue delay
        self.next_fatigue_time = time.time() + random.uniform(
            self.fatigue_trigger_min_time, self.fatigue_trigger_max_time
        )
        logging.info("Fatigue reset")

    def perform_click(self):
        # Random interval between clicks with a minimum interval
        interval = self.randomize_normal(
            self.click_interval + self.click_fatigue, self.click_interval_randomness
        )
        interval = max(self.click_interval_min, interval)
        logging.info(f"Interval between clicks: {interval:.3f} seconds")
        time.sleep(interval)

        # Perform the click and hold for a random duration with a minimum hold time
        hold_time = self.randomize_normal(
            self.hold_time + self.hold_fatigue,
            self.hold_time_randomness,
        )
        hold_time = max(self.hold_time_min, hold_time)
        x, y = pyautogui.position()
        pyautogui.mouseDown()
        logging.info(f"Click hold time: {hold_time:.3f} seconds")
        self.display_click_position(x, y)
        time.sleep(hold_time)
        pyautogui.mouseUp()

    def display_click_position(self, x, y):
        # Create a temporary Tkinter window to display the click position
        click_window = tk.Tk()
        click_window.overrideredirect(True)  # Remove window decorations
        click_window.geometry(f"10x10+{x}+{y}")  # Set size and position
        click_window.attributes("-topmost", True)  # Keep the window on top

        canvas = tk.Canvas(click_window, width=10, height=10, bg="red")
        canvas.pack()

        click_window.after(100, click_window.destroy)  # Destroy after 100 ms

        click_window.mainloop()

    def handle_fatigue_delay(self):
        # Simulate human click fatigue delay
        if self.accumulated_click_fatigue_delay > 0:
            fatigue_delay = min(
                self.accumulated_click_fatigue_delay,
                self.randomize_normal(
                    self.click_interval, self.click_interval_randomness
                ),
            )
            fatigue_delay = max(self.click_interval_min, fatigue_delay)
            self.accumulated_click_fatigue_delay -= fatigue_delay
            logging.info(f"Click fatigue delay: {fatigue_delay:.3f} seconds")
            time.sleep(fatigue_delay)

        # Simulate human hold fatigue delay
        if self.accumulated_hold_fatigue_delay > 0:
            fatigue_delay = min(
                self.accumulated_hold_fatigue_delay,
                self.randomize_normal(self.hold_time, self.hold_time_randomness),
            )
            fatigue_delay = max(self.hold_time_min, fatigue_delay)
            self.accumulated_hold_fatigue_delay -= fatigue_delay
            logging.info(f"Hold fatigue delay: {fatigue_delay:.3f} seconds")
            time.sleep(fatigue_delay)

    def take_short_break(self, start_time):
        short_break = self.randomize_uniform(
            self.short_break_duration, self.short_break_duration_randomness
        )
        short_break = max(self.click_interval_min, short_break)
        total_runtime = time.time() - start_time
        time_since_last_short_break = time.time() - self.last_short_break_time
        time_since_last_long_break = time.time() - self.last_long_break_time
        logging.info(f"Taking short break: {short_break:.3f} seconds")
        logging.info(
            f"Time since last short break: {time_since_last_short_break:.3f} seconds"
        )
        logging.info(
            f"Time since last long break: {time_since_last_long_break:.3f} seconds"
        )
        logging.info(f"Total runtime: {total_runtime:.3f} seconds")
        time.sleep(short_break)
        self.last_short_break_time = time.time()

    def take_long_break(self, start_time):
        long_break = self.randomize_uniform(
            self.long_break_duration, self.long_break_duration_randomness
        )
        long_break = max(self.click_interval_min, long_break)
        total_runtime = time.time() - start_time
        time_since_last_short_break = time.time() - self.last_short_break_time
        time_since_last_long_break = time.time() - self.last_long_break_time
        logging.info(f"Taking long break: {long_break:.3f} seconds")
        logging.info(
            f"Time since last short break: {time_since_last_short_break:.3f} seconds"
        )
        logging.info(
            f"Time since last long break: {time_since_last_long_break:.3f} seconds"
        )
        logging.info(f"Total runtime: {total_runtime:.3f} seconds")
        time.sleep(long_break)
        self.reset_fatigue()
        self.last_long_break_time = time.time()
        self.next_long_break_time = time.time() + random.uniform(
            self.long_break_trigger_min_time, self.long_break_trigger_max_time
        )

    def click_like_human(self):
        start_time = time.time()
        self.running = True
        while (time.time() - start_time) < self.max_runtime and self.running:
            self.update_fatigue()
            self.perform_click()
            self.handle_fatigue_delay()

            # Simulate short breaks
            if random.random() < 0.002:
                self.take_short_break(start_time)

            # Simulate long breaks
            current_time = time.time()
            if current_time >= self.next_long_break_time:
                self.take_long_break(start_time)

    def start(self):
        self.click_like_human()

    def stop(self):
        self.running = False

    def prevent_mouse_movement_function(self):
        initial_position = pyautogui.position()
        while self.prevent_mouse_movement:
            pyautogui.moveTo(initial_position)
            time.sleep(0.01)


if __name__ == "__main__":
    autoclicker = AutoClicker()
    autoclicker.start()
