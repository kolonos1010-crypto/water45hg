"""
Configuration module for Phone Automation Controller.

Handles user settings: menu option, API key, file paths, bot count,
target window title, and timeouts. Provides masked input for secrets
and validation for all fields.
"""

import getpass
import os
import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional


CONFIG_FILE = "automation_config.json"


@dataclass
class AutomationConfig:
    """All user-configurable settings for the automation run."""

    menu_option: str = "1"
    api_key: str = ""
    file_paths: List[str] = field(default_factory=list)
    bot_count: str = "9495"
    window_title: str = ""
    step_timeout: float = 30.0  # seconds to wait for each prompt
    poll_interval: float = 0.5  # seconds between screen polls
    typing_delay: float = 0.03  # seconds between simulated keystrokes
    pause_key: str = "f9"  # hotkey to pause/resume

    def validate(self) -> List[str]:
        """Return a list of validation error messages (empty = valid)."""
        errors: List[str] = []

        if not self.menu_option.strip():
            errors.append("Menu option cannot be empty.")

        if not self.api_key.strip():
            errors.append("API key cannot be empty.")

        if not self.file_paths:
            errors.append("At least one file path is required.")
        for fp in self.file_paths:
            if not os.path.isfile(fp):
                errors.append(f"File not found: {fp}")

        if not self.bot_count.strip().isdigit():
            errors.append("Bot count must be a positive integer.")

        if not self.window_title.strip():
            errors.append("Target window title cannot be empty.")

        return errors

    def save(self, path: str = CONFIG_FILE) -> None:
        """Persist config to disk (API key excluded for safety)."""
        data = asdict(self)
        data.pop("api_key", None)  # never persist the key
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: str = CONFIG_FILE) -> "AutomationConfig":
        """Load config from disk. Missing fields use defaults."""
        if not os.path.isfile(path):
            return cls()
        with open(path, "r") as f:
            data = json.load(f)
        data.pop("api_key", None)
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def prompt_config() -> AutomationConfig:
    """Interactive CLI wizard that walks the user through configuration."""

    cfg = AutomationConfig()

    print("\n" + "=" * 60)
    print("   PHONE AUTOMATION CONTROLLER - Configuration")
    print("=" * 60)

    # --- Menu option ---
    val = input(f"\n[1] Menu option to select (default: {cfg.menu_option}): ").strip()
    if val:
        cfg.menu_option = val

    # --- API key (masked) ---
    while True:
        key = getpass.getpass("[2] API key (input hidden): ")
        if key.strip():
            cfg.api_key = key.strip()
            break
        print("    API key cannot be empty. Try again.")

    # --- File paths ---
    print("\n[3] File paths to process (enter one per line, blank line to finish):")
    while True:
        fp = input("    File path: ").strip()
        if not fp:
            if cfg.file_paths:
                break
            print("    At least one file is required.")
            continue
        # Allow user to paste paths with quotes
        fp = fp.strip("\"'")
        if os.path.isfile(fp):
            cfg.file_paths.append(fp)
            print(f"    Added: {fp}")
        else:
            print(f"    WARNING: File not found: {fp}")
            add_anyway = input("    Add anyway? (y/n): ").strip().lower()
            if add_anyway == "y":
                cfg.file_paths.append(fp)

    # --- Bot count ---
    val = input(f"\n[4] Number of bots (default: {cfg.bot_count}): ").strip()
    if val:
        cfg.bot_count = val

    # --- Target window title ---
    while True:
        title = input("[5] Target application window title (or partial match): ").strip()
        if title:
            cfg.window_title = title
            break
        print("    Window title cannot be empty.")

    # --- Timeouts ---
    val = input(f"\n[6] Step timeout in seconds (default: {cfg.step_timeout}): ").strip()
    if val:
        try:
            cfg.step_timeout = float(val)
        except ValueError:
            print("    Invalid number, keeping default.")

    val = input(f"[7] Typing delay in seconds (default: {cfg.typing_delay}): ").strip()
    if val:
        try:
            cfg.typing_delay = float(val)
        except ValueError:
            print("    Invalid number, keeping default.")

    return cfg


def display_config(cfg: AutomationConfig) -> None:
    """Pretty-print the current configuration (masking the API key)."""
    masked_key = cfg.api_key[:4] + "*" * (len(cfg.api_key) - 4) if len(cfg.api_key) > 4 else "****"
    print("\n" + "-" * 50)
    print("  Current Configuration")
    print("-" * 50)
    print(f"  Menu option   : {cfg.menu_option}")
    print(f"  API key       : {masked_key}")
    print(f"  Files         : {len(cfg.file_paths)} file(s)")
    for i, fp in enumerate(cfg.file_paths, 1):
        print(f"                  {i}. {fp}")
    print(f"  Bot count     : {cfg.bot_count}")
    print(f"  Window title  : {cfg.window_title}")
    print(f"  Step timeout  : {cfg.step_timeout}s")
    print(f"  Typing delay  : {cfg.typing_delay}s")
    print(f"  Pause hotkey  : {cfg.pause_key}")
    print("-" * 50)
