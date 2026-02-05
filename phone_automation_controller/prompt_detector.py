"""
Prompt detection / screen reading module.

Monitors the target application's console output for known prompt
strings, error messages, and status lines. Uses a combination of:

1. Clipboard-based reading (select-all + copy from the console)
2. Win32 console buffer reading (Windows only)
3. Configurable polling with timeout

Also detects API rate-limit / max-out errors to halt the process.
"""

import re
import time
import platform
import subprocess
from typing import Optional, List, Tuple
from dataclasses import dataclass

try:
    import pyautogui
except ImportError:
    pyautogui = None  # type: ignore[assignment]

SYSTEM = platform.system()


# ---------------------------------------------------------------------------
# Known prompt patterns
# ---------------------------------------------------------------------------

PROMPT_CHOICE = re.compile(r"\[\*\]\s*Your choice\s*:", re.IGNORECASE)
PROMPT_API_KEY = re.compile(r"(api[_ ]?key|enter.*key|key\s*:)", re.IGNORECASE)
PROMPT_FILE = re.compile(r"press enter to open.*numbers file", re.IGNORECASE)
PROMPT_BOTS = re.compile(r"how many bots\s*:", re.IGNORECASE)

# Error / rate-limit patterns
ERROR_INVALID_KEY = re.compile(r"invalid api key", re.IGNORECASE)
ERROR_RATE_LIMIT = re.compile(
    r"(rate.?limit|too many requests|api.?max|quota.?exceeded|429|limit reached)",
    re.IGNORECASE,
)
ERROR_GENERIC = re.compile(r"(error|failed|exception)", re.IGNORECASE)

# Processing-complete patterns
PROCESSING_LOADED = re.compile(r"loaded\s*\[\d+\]", re.IGNORECASE)
PROCESSING_DONE = re.compile(r"(completed|finished|done)", re.IGNORECASE)


@dataclass
class DetectionResult:
    """Result of scanning the console output."""

    matched_prompt: Optional[str] = None  # which prompt was found
    full_text: str = ""  # the raw text that was read
    is_error: bool = False
    error_message: str = ""
    is_rate_limited: bool = False


class PromptDetector:
    """Polls the target window's console text and matches prompts."""

    def __init__(
        self,
        poll_interval: float = 0.5,
        timeout: float = 30.0,
    ):
        self.poll_interval = poll_interval
        self.timeout = timeout
        self._last_text = ""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def wait_for_prompt(
        self,
        prompt_pattern: re.Pattern,
        timeout: Optional[float] = None,
        window_id: Optional[str] = None,
    ) -> DetectionResult:
        """Block until *prompt_pattern* appears or timeout expires.

        Returns a ``DetectionResult`` with the match details.
        Also checks for error / rate-limit patterns on every poll.
        """
        deadline = time.time() + (timeout or self.timeout)

        while time.time() < deadline:
            text = self._read_console_text(window_id)
            if not text:
                time.sleep(self.poll_interval)
                continue

            # Check rate-limit first — highest priority
            if ERROR_RATE_LIMIT.search(text) and text != self._last_text:
                self._last_text = text
                return DetectionResult(
                    full_text=text,
                    is_error=True,
                    is_rate_limited=True,
                    error_message="API rate limit detected — stopping.",
                )

            # Check for invalid key error
            if ERROR_INVALID_KEY.search(text) and text != self._last_text:
                self._last_text = text
                return DetectionResult(
                    full_text=text,
                    is_error=True,
                    error_message="Invalid API key detected.",
                )

            # Check for the target prompt
            if prompt_pattern.search(text):
                new_text = text[len(self._last_text):] if text.startswith(self._last_text) else text
                if prompt_pattern.search(new_text) or self._last_text == "":
                    self._last_text = text
                    return DetectionResult(
                        matched_prompt=prompt_pattern.pattern,
                        full_text=text,
                    )

            time.sleep(self.poll_interval)

        # Timeout
        return DetectionResult(
            full_text=self._last_text,
            is_error=True,
            error_message=f"Timeout ({timeout or self.timeout}s) waiting for prompt: {prompt_pattern.pattern}",
        )

    def wait_for_any_prompt(
        self,
        patterns: List[Tuple[str, re.Pattern]],
        timeout: Optional[float] = None,
        window_id: Optional[str] = None,
    ) -> Tuple[Optional[str], DetectionResult]:
        """Wait for any one of several named patterns.

        *patterns* is a list of (name, regex) tuples.
        Returns (matched_name, DetectionResult).
        """
        deadline = time.time() + (timeout or self.timeout)

        while time.time() < deadline:
            text = self._read_console_text(window_id)
            if not text:
                time.sleep(self.poll_interval)
                continue

            if ERROR_RATE_LIMIT.search(text) and text != self._last_text:
                self._last_text = text
                result = DetectionResult(
                    full_text=text,
                    is_error=True,
                    is_rate_limited=True,
                    error_message="API rate limit detected — stopping.",
                )
                return (None, result)

            for name, pattern in patterns:
                new_text = text[len(self._last_text):] if text.startswith(self._last_text) else text
                if pattern.search(new_text) or (self._last_text == "" and pattern.search(text)):
                    self._last_text = text
                    result = DetectionResult(
                        matched_prompt=name,
                        full_text=text,
                    )
                    return (name, result)

            time.sleep(self.poll_interval)

        result = DetectionResult(
            full_text=self._last_text,
            is_error=True,
            error_message=f"Timeout waiting for any prompt.",
        )
        return (None, result)

    def check_for_rate_limit(self, window_id: Optional[str] = None) -> bool:
        """Quick one-shot check for rate-limit text."""
        text = self._read_console_text(window_id)
        if text and ERROR_RATE_LIMIT.search(text):
            return True
        return False

    def reset(self) -> None:
        """Clear stored text state between runs."""
        self._last_text = ""

    # ------------------------------------------------------------------
    # Console text reading
    # ------------------------------------------------------------------

    def _read_console_text(self, window_id: Optional[str] = None) -> Optional[str]:
        """Best-effort read of the console's visible text.

        Strategy:
        1. On Windows, try the console buffer API first.
        2. Fall back to select-all + clipboard copy (works cross-platform
           for terminal emulators that support Ctrl+A / Cmd+A).
        """
        if SYSTEM == "Windows" and window_id:
            text = self._read_windows_console_buffer(window_id)
            if text:
                return text

        # Clipboard approach — works in most terminals
        return self._read_via_clipboard()

    @staticmethod
    def _read_windows_console_buffer(window_id: str) -> Optional[str]:
        """Read characters from the Windows console buffer."""
        try:
            from phone_automation_controller.window_manager import get_window_text
            return get_window_text(window_id)
        except Exception:
            return None

    @staticmethod
    def _read_via_clipboard() -> Optional[str]:
        """Select all text in the focused console, copy, and return it.

        Restores the previous clipboard content afterwards.
        """
        if pyautogui is None:
            return None

        try:
            import pyperclip
        except ImportError:
            return None

        try:
            old_clipboard = pyperclip.paste()
        except Exception:
            old_clipboard = ""

        try:
            # Select all
            if SYSTEM == "Darwin":
                pyautogui.hotkey("command", "a")
            else:
                pyautogui.hotkey("ctrl", "a")
            time.sleep(0.1)

            # Copy
            if SYSTEM == "Darwin":
                pyautogui.hotkey("command", "c")
            else:
                pyautogui.hotkey("ctrl", "shift", "c")  # many Linux terminals
            time.sleep(0.1)

            text = pyperclip.paste()

            # Deselect
            pyautogui.press("right")

            return text if text != old_clipboard else None
        except Exception:
            return None
        finally:
            # Restore clipboard
            try:
                if old_clipboard:
                    pyperclip.copy(old_clipboard)
            except Exception:
                pass
