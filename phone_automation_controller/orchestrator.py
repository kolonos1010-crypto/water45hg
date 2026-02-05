"""
Automation orchestrator — the main flow controller.

Executes the full automation sequence:
  1. Find and focus the target window
  2. Send menu choice
  3. Send API key
  4. For each file: send file path, wait for processing, send bot count
  5. Monitor for rate-limit errors and stop if detected
  6. Support pause / resume via hotkey

All steps are driven by prompt detection (not blind timers).
"""

import sys
import time
import threading
from typing import Optional

from phone_automation_controller.config import AutomationConfig, display_config
from phone_automation_controller.window_manager import find_window, focus_window
from phone_automation_controller.input_simulator import InputSimulator
from phone_automation_controller.prompt_detector import (
    PromptDetector,
    PROMPT_CHOICE,
    PROMPT_API_KEY,
    PROMPT_FILE,
    PROMPT_BOTS,
    ERROR_RATE_LIMIT,
)


class AutomationOrchestrator:
    """Drives the target application through its prompt sequence."""

    def __init__(self, config: AutomationConfig):
        self.cfg = config
        self.simulator = InputSimulator(typing_delay=config.typing_delay)
        self.detector = PromptDetector(
            poll_interval=config.poll_interval,
            timeout=config.step_timeout,
        )
        self.window_id: Optional[str] = None

        # Pause / resume state
        self._paused = False
        self._stop_requested = False
        self._pause_lock = threading.Lock()

        # Stats
        self.files_processed = 0
        self.files_total = len(config.file_paths)

    # ------------------------------------------------------------------
    # Pause / stop controls
    # ------------------------------------------------------------------

    def request_pause(self) -> None:
        with self._pause_lock:
            self._paused = True
        self._status("PAUSED — press the pause key again to resume.")

    def request_resume(self) -> None:
        with self._pause_lock:
            self._paused = False
        self._status("RESUMED.")

    def toggle_pause(self) -> None:
        with self._pause_lock:
            self._paused = not self._paused
        if self._paused:
            self._status("PAUSED — press the pause key again to resume.")
        else:
            self._status("RESUMED.")

    def request_stop(self) -> None:
        self._stop_requested = True
        self._status("STOP requested — finishing current step…")

    @property
    def is_paused(self) -> bool:
        with self._pause_lock:
            return self._paused

    def _wait_while_paused(self) -> None:
        """Block while the pause flag is set."""
        while self.is_paused and not self._stop_requested:
            time.sleep(0.3)

    # ------------------------------------------------------------------
    # Main execution
    # ------------------------------------------------------------------

    def run(self) -> bool:
        """Execute the full automation flow. Returns True on success."""

        self._status("Starting automation…")
        display_config(self.cfg)

        # Step 0: Find and focus the target window
        if not self._step_focus_window():
            return False

        # Step 1: Menu choice
        if not self._step_menu_choice():
            return False

        # Step 2: API key
        if not self._step_api_key():
            return False

        # Step 3-N: Process each file
        for i, file_path in enumerate(self.cfg.file_paths):
            if self._stop_requested:
                self._status("Stopped by user.")
                return False

            self._wait_while_paused()

            self._status(f"\n--- File {i + 1}/{self.files_total}: {file_path} ---")

            if not self._step_file_selection(file_path):
                return False

            if not self._step_bot_count():
                return False

            self.files_processed += 1
            self._status(
                f"File {i + 1}/{self.files_total} complete. "
                f"({self.files_processed} processed so far)"
            )

            # If there are more files, wait for the next cycle prompt
            if i < len(self.cfg.file_paths) - 1:
                self._status("Waiting for next cycle…")
                result = self.detector.wait_for_prompt(
                    PROMPT_FILE, timeout=self.cfg.step_timeout, window_id=self.window_id
                )
                if result.is_rate_limited:
                    self._error("API rate limit reached — stopping.")
                    return False
                if result.is_error:
                    self._error(f"Error waiting for next file prompt: {result.error_message}")
                    return False

        self._status(f"\nAll {self.files_total} file(s) processed successfully.")
        return True

    # ------------------------------------------------------------------
    # Individual steps
    # ------------------------------------------------------------------

    def _step_focus_window(self) -> bool:
        self._status(f"Looking for window: '{self.cfg.window_title}'")
        self.window_id = find_window(self.cfg.window_title)
        if not self.window_id:
            self._error(
                f"Could not find window with title containing '{self.cfg.window_title}'.\n"
                "Make sure the target application is running."
            )
            return False

        if not focus_window(self.window_id):
            self._error("Found the window but could not bring it to the foreground.")
            return False

        self._status("Target window focused.")
        return True

    def _step_menu_choice(self) -> bool:
        self._wait_while_paused()
        if self._stop_requested:
            return False

        self._status("Waiting for menu prompt '[*] Your choice :'…")
        result = self.detector.wait_for_prompt(
            PROMPT_CHOICE, timeout=self.cfg.step_timeout, window_id=self.window_id
        )
        if result.is_rate_limited:
            self._error("API rate limit reached — stopping.")
            return False
        if result.is_error:
            self._error(f"Menu prompt not detected: {result.error_message}")
            return False

        self._status(f"Sending menu option: {self.cfg.menu_option}")
        focus_window(self.window_id)
        time.sleep(0.2)
        self.simulator.type_and_enter(self.cfg.menu_option)
        self._status("Menu option sent.")
        return True

    def _step_api_key(self) -> bool:
        self._wait_while_paused()
        if self._stop_requested:
            return False

        self._status("Waiting for API key prompt…")
        result = self.detector.wait_for_prompt(
            PROMPT_API_KEY, timeout=self.cfg.step_timeout, window_id=self.window_id
        )
        if result.is_rate_limited:
            self._error("API rate limit reached — stopping.")
            return False
        if result.is_error:
            self._error(f"API key prompt not detected: {result.error_message}")
            return False

        self._status("Sending API key…")
        focus_window(self.window_id)
        time.sleep(0.2)
        self.simulator.type_and_enter(self.cfg.api_key)
        self._status("API key sent. Waiting for verification…")

        # Brief pause to check for invalid key error
        time.sleep(2)
        if self.detector.check_for_rate_limit(self.window_id):
            self._error("API rate limit reached — stopping.")
            return False

        return True

    def _step_file_selection(self, file_path: str) -> bool:
        self._wait_while_paused()
        if self._stop_requested:
            return False

        self._status("Waiting for file selection prompt…")
        result = self.detector.wait_for_prompt(
            PROMPT_FILE, timeout=self.cfg.step_timeout, window_id=self.window_id
        )
        if result.is_rate_limited:
            self._error("API rate limit reached — stopping.")
            return False
        if result.is_error:
            self._error(f"File prompt not detected: {result.error_message}")
            return False

        self._status(f"Sending Enter to open file dialog…")
        focus_window(self.window_id)
        time.sleep(0.2)
        self.simulator.send_enter()

        # Wait for the file dialog to appear, then type path
        self._status(f"Sending file path: {file_path}")
        time.sleep(1.0)
        self.simulator.send_file_path_to_dialog(file_path)
        self._status("File path sent.")

        # Wait for processing status
        time.sleep(2)
        return True

    def _step_bot_count(self) -> bool:
        self._wait_while_paused()
        if self._stop_requested:
            return False

        self._status("Waiting for 'How many bots' prompt…")
        result = self.detector.wait_for_prompt(
            PROMPT_BOTS, timeout=self.cfg.step_timeout, window_id=self.window_id
        )
        if result.is_rate_limited:
            self._error("API rate limit reached — stopping.")
            return False
        if result.is_error:
            self._error(f"Bot prompt not detected: {result.error_message}")
            return False

        self._status(f"Sending bot count: {self.cfg.bot_count}")
        focus_window(self.window_id)
        time.sleep(0.2)
        self.simulator.type_and_enter(self.cfg.bot_count)
        self._status("Bot count sent. Processing…")

        # Monitor for rate limit during processing
        check_deadline = time.time() + self.cfg.step_timeout
        while time.time() < check_deadline:
            if self._stop_requested:
                return False
            if self.detector.check_for_rate_limit(self.window_id):
                self._error("API rate limit reached during processing — stopping.")
                return False
            time.sleep(2)
            # Check if processing seems done (next prompt appeared)
            break  # Single check pass — the next step's wait_for_prompt handles continuation

        return True

    # ------------------------------------------------------------------
    # Output helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _status(msg: str) -> None:
        print(f"  [STATUS] {msg}")

    @staticmethod
    def _error(msg: str) -> None:
        print(f"  [ERROR]  {msg}", file=sys.stderr)
