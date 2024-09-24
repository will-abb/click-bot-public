# AutoClicker Application

## Purpose
The AutoClicker application is designed to automate mouse clicks with human-like behavior. This can be useful for repetitive tasks that require constant clicking.

## Parameters
- **click_interval**: Base interval between clicks in seconds.
- **click_interval_randomness**: Randomness added/subtracted to the base click interval in seconds.
- **click_interval_min**: Minimum interval between clicks in seconds.
- **click_fatigue_increase**: Amount by which click interval cumulatively increases due to fatigue in seconds.
- **hold_time**: Base duration to hold the click in seconds.
- **hold_time_randomness**: Randomness added to the base hold duration in seconds.
- **hold_time_min**: Minimum time the click is held in seconds.
- **hold_fatigue_increase**: Amount by which hold duration cumulatively increases due to fatigue in seconds.
- **fatigue_trigger_min_time**: Minimum interval for fatigue increase in seconds.
- **fatigue_trigger_max_time**: Maximum interval for fatigue increase in seconds.
- **short_break_duration**: Base duration for short breaks in seconds.
- **short_break_duration_randomness**: Randomness added to the base short break duration in seconds.
- **long_break_trigger_min_time**: Minimum interval between long breaks in seconds.
- **long_break_trigger_max_time**: Maximum interval between long breaks in seconds.
- **long_break_duration**: Base duration for long breaks in seconds.
- **long_break_duration_randomness**: Randomness added to the base long break duration in seconds.
- **max_runtime**: Maximum runtime for the script in seconds.

## How It Works
The AutoClicker simulates mouse clicks at random intervals within specified ranges to mimic human behavior. It also includes functionality for fatigue and breaks, ensuring the clicking pattern appears natural.

## Hotkeys
- **Hotkey**: The key to start/stop the AutoClicker. Default is F1, but it can be changed.

## Logging
All actions are logged to a file (`autoclicker.log`) and can be viewed in real-time through the log viewer.
