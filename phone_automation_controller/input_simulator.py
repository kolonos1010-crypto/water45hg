"""
Input simulation engine.

Sends keystrokes, text, and special keys to the currently focused window
using pyautogui (cross-platform). Includes safety mechanisms and
configurable delays.
"""

import time
import platform
from typing import Optional

try:
    import pyautogui

    pyautogui.FAILSAFE = True  # move mouse to top-left corner to abort
    pyautogui.PAUSE = 0.02
except ImportError:
    pyautogui = None  # type: ignore[assignment]

SYSTEM = platform.system()


class InputSimulator:
    """Sends simulated keyboard input to the focused window."""

    def __init__(self, typing_delay: float = 0.03):
        self.typing_delay = typing_delay
        self._check_backend()

    # ------------------------------------------------------------------
    # Backend availability
    # ------------------------------------------------------------------

    @staticmethod
    def _check_backend() -> None:
        if pyautogui is None:
            raise RuntimeError(
                "pyautogui is not installed. "
                "Install it with: pip install pyautogui"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def type_text(self, text: str, delay: Optional[float] = None) -> None:
        """Type *text* character by character with an inter-key delay.

        Uses pyautogui.write for ASCII-safe text, falls back to
        pyperclip + paste for Unicode.
        """
        interval = delay if delay is not None else self.typing_delay

        if _is_ascii(text):
            pyautogui.write(text, interval=interval)
        else:
            # For non-ASCII text, use clipboard paste
            self._paste_text(text)

    def send_key(self, key: str) -> None:
        """Send a single special key (e.g. 'enter', 'tab', 'escape')."""
        pyautogui.press(key)

    def send_enter(self) -> None:
        """Press the Enter key."""
        pyautogui.press("enter")

    def send_hotkey(self, *keys: str) -> None:
        """Send a hotkey combo (e.g. send_hotkey('ctrl', 'v'))."""
        pyautogui.hotkey(*keys)

    def type_and_enter(self, text: str, delay: Optional[float] = None) -> None:
        """Type *text* then press Enter."""
        self.type_text(text, delay=delay)
        time.sleep(0.1)
        self.send_enter()

    def send_file_path_to_dialog(self, file_path: str) -> None:
        """Type a file path into a file-open dialog and confirm.

        On Windows this types directly into the filename field.
        A short delay is added to let the dialog render.
        """
        time.sleep(0.5)  # wait for dialog to open
        self.type_text(file_path, delay=0.02)
        time.sleep(0.2)
        self.send_enter()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _paste_text(text: str) -> None:
        """Place *text* on the clipboard and paste it."""
        try:
            import pyperclip
            pyperclip.copy(text)
        except ImportError:
            # Fallback: write to clipboard via pyautogui internals
            # This works on most platforms with xclip / pbcopy
            import subprocess

            if SYSTEM == "Darwin":
                proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
                proc.communicate(text.encode("utf-8"))
            elif SYSTEM == "Linux":
                proc = subprocess.Popen(
                    ["xclip", "-selection", "clipboard"],
                    stdin=subprocess.PIPE,
                )
                proc.communicate(text.encode("utf-8"))
            else:
                # Windows fallback handled by pyperclip normally being available
                raise RuntimeError("Cannot paste text: install pyperclip")

        if SYSTEM == "Darwin":
            pyautogui.hotkey("command", "v")
        else:
            pyautogui.hotkey("ctrl", "v")

        time.sleep(0.1)


def _is_ascii(text: str) -> bool:
    try:
        text.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False
