"""
CLI entry point for Phone Automation Controller.

Run with:
    python -m phone_automation_controller
"""

import sys
import threading
import signal

from phone_automation_controller.config import (
    AutomationConfig,
    prompt_config,
    display_config,
)
from phone_automation_controller.orchestrator import AutomationOrchestrator
from phone_automation_controller.window_manager import list_windows


BANNER = r"""
  ====================================================
   Phone Automation Controller
   External input-simulation tool for phone-number
   processing software.
  ====================================================
"""


def main() -> None:
    print(BANNER)

    while True:
        print("\n  Main Menu")
        print("  ---------")
        print("  1. Configure and run automation")
        print("  2. List visible windows (helper)")
        print("  3. Run with saved config (automation_config.json)")
        print("  4. Exit")
        choice = input("\n  Select an option [1-4]: ").strip()

        if choice == "1":
            _configure_and_run()
        elif choice == "2":
            _list_windows()
        elif choice == "3":
            _run_saved_config()
        elif choice == "4":
            print("\n  Goodbye.\n")
            sys.exit(0)
        else:
            print("  Invalid option. Try again.")


# ----------------------------------------------------------------------
# Menu handlers
# ----------------------------------------------------------------------

def _configure_and_run() -> None:
    """Walk through configuration then execute."""
    cfg = prompt_config()
    errors = cfg.validate()

    if errors:
        print("\n  Configuration errors:")
        for e in errors:
            print(f"    - {e}")
        fix = input("\n  Continue anyway? (y/n): ").strip().lower()
        if fix != "y":
            return

    display_config(cfg)

    save = input("\n  Save config for future runs? (y/n): ").strip().lower()
    if save == "y":
        cfg.save()
        print("  Config saved to automation_config.json (API key excluded).")

    confirm = input("\n  Start automation now? (y/n): ").strip().lower()
    if confirm != "y":
        return

    _execute(cfg)


def _run_saved_config() -> None:
    """Load config from disk, prompt for API key, then run."""
    import getpass

    try:
        cfg = AutomationConfig.load()
    except Exception as exc:
        print(f"  Could not load config: {exc}")
        return

    if not cfg.file_paths:
        print("  Saved config has no file paths. Use option 1 to configure.")
        return

    print("\n  Loaded saved configuration:")
    # Need API key (never saved)
    while True:
        key = getpass.getpass("  Enter API key (hidden): ")
        if key.strip():
            cfg.api_key = key.strip()
            break
        print("  API key cannot be empty.")

    display_config(cfg)
    confirm = input("\n  Start automation now? (y/n): ").strip().lower()
    if confirm != "y":
        return

    _execute(cfg)


def _list_windows() -> None:
    """Show visible windows to help user pick the right title."""
    search = input("\n  Filter by title (blank for all): ").strip() or None
    windows = list_windows(search)
    if not windows:
        print("  No windows found. Make sure the target application is running.")
        return
    print(f"\n  Found {len(windows)} window(s):")
    for i, title in enumerate(windows, 1):
        print(f"    {i}. {title}")


# ----------------------------------------------------------------------
# Execution
# ----------------------------------------------------------------------

def _execute(cfg: AutomationConfig) -> None:
    """Set up the orchestrator, hotkey listener, and run."""
    orch = AutomationOrchestrator(cfg)

    # Register Ctrl+C handler
    def _sigint_handler(_sig, _frame):
        print("\n  [CTRL+C] Stopping automation…")
        orch.request_stop()

    signal.signal(signal.SIGINT, _sigint_handler)

    # Optional: pause hotkey listener using the 'keyboard' library
    _start_hotkey_listener(cfg.pause_key, orch)

    print(f"\n  Automation starting. Press {cfg.pause_key.upper()} to pause/resume, Ctrl+C to stop.\n")

    success = orch.run()

    if success:
        print("\n  ========================================")
        print("  Automation completed successfully.")
        print(f"  Files processed: {orch.files_processed}/{orch.files_total}")
        print("  ========================================\n")
    else:
        print("\n  ========================================")
        print("  Automation stopped or encountered an error.")
        print(f"  Files processed: {orch.files_processed}/{orch.files_total}")
        print("  ========================================\n")


def _start_hotkey_listener(pause_key: str, orch: AutomationOrchestrator) -> None:
    """Try to register a global hotkey for pause/resume."""
    try:
        import keyboard

        keyboard.add_hotkey(pause_key, orch.toggle_pause)
    except ImportError:
        print(
            f"  NOTE: 'keyboard' library not installed. "
            f"Pause hotkey ({pause_key}) unavailable.\n"
            f"  Install with: pip install keyboard"
        )
    except Exception as exc:
        print(f"  NOTE: Could not register pause hotkey: {exc}")


# ----------------------------------------------------------------------

if __name__ == "__main__":
    main()
