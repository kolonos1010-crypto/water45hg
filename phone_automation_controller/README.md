# Phone Automation Controller

Standalone command-line tool that automates input to an external phone-number
processing application using system-level keystroke simulation.

This tool does **not** modify the target software — it runs in its own terminal
and drives the target application by detecting prompts and sending keystrokes.

## Quick Start

```bash
# Install dependencies
pip install -r phone_automation_controller/requirements.txt

# Run
python -m phone_automation_controller
```

## How It Works

1. You configure the automation (API key, file paths, bot count, target window title).
2. The tool finds and focuses the target application's window.
3. It watches for specific prompts in the target app and sends the right input at the right time.
4. If the API hits a rate limit, the tool stops automatically.

## Prompt Sequence Handled

| Target App Prompt | Automation Action |
|---|---|
| `[*] Your choice :` | Sends configured menu option |
| API key prompt | Sends configured API key (masked in config) |
| `Press Enter to open your Numbers file :` | Sends Enter, then types file path in dialog |
| `How many bots :` | Sends configured bot count |

## Controls

- **F9** (default) — Pause / resume automation
- **Ctrl+C** — Stop automation immediately

## Configuration

On first run, the tool walks you through an interactive setup wizard.
Settings (except the API key) can be saved to `automation_config.json` for reuse.

## Requirements

- **Python 3.8+**
- **pyautogui** — cross-platform keystroke simulation
- **pyperclip** — clipboard access for screen reading
- **keyboard** — global hotkey for pause/resume (optional)
- **pygetwindow** — window management (Windows only)
- On Linux: `wmctrl` or `xdotool` for window management
- On macOS: Accessibility permissions must be granted to your terminal

## Project Structure

```
phone_automation_controller/
├── __init__.py          # Package marker
├── __main__.py          # CLI entry point & menu
├── config.py            # User configuration wizard & persistence
├── window_manager.py    # Find, focus, read target windows
├── input_simulator.py   # Keystroke simulation engine
├── prompt_detector.py   # Console text polling & prompt matching
├── orchestrator.py      # Main automation flow controller
├── requirements.txt     # Python dependencies
└── README.md            # This file
```
