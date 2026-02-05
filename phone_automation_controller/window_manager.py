"""
Window management module.

Finds, focuses, and reads text from the target application's console
window using cross-platform approaches:
  - Windows: pygetwindow + win32gui
  - Linux:   wmctrl / xdotool (subprocess)
  - macOS:   osascript (subprocess)
"""

import platform
import subprocess
import time
from typing import Optional, List


SYSTEM = platform.system()  # "Windows", "Linux", "Darwin"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def find_window(title_substring: str) -> Optional[str]:
    """Return a window identifier whose title contains *title_substring*.

    Returns the window handle (Windows), X window id (Linux), or
    window name (macOS).  Returns ``None`` if no match is found.
    """
    if SYSTEM == "Windows":
        return _find_window_windows(title_substring)
    elif SYSTEM == "Linux":
        return _find_window_linux(title_substring)
    elif SYSTEM == "Darwin":
        return _find_window_macos(title_substring)
    return None


def focus_window(window_id: str) -> bool:
    """Bring the window identified by *window_id* to the foreground.

    Returns ``True`` on success.
    """
    if SYSTEM == "Windows":
        return _focus_window_windows(window_id)
    elif SYSTEM == "Linux":
        return _focus_window_linux(window_id)
    elif SYSTEM == "Darwin":
        return _focus_window_macos(window_id)
    return False


def list_windows(title_filter: Optional[str] = None) -> List[str]:
    """Return a list of visible window titles, optionally filtered."""
    if SYSTEM == "Windows":
        return _list_windows_windows(title_filter)
    elif SYSTEM == "Linux":
        return _list_windows_linux(title_filter)
    elif SYSTEM == "Darwin":
        return _list_windows_macos(title_filter)
    return []


def get_window_text(window_id: str) -> Optional[str]:
    """Attempt to read the visible text of the target console window.

    This is a best-effort operation. On Windows we can use the console
    buffer API; on Linux / macOS we rely on clipboard / accessibility
    approaches.
    """
    if SYSTEM == "Windows":
        return _get_window_text_windows(window_id)
    return None  # non-Windows falls back to clipboard approach in reader


# ---------------------------------------------------------------------------
# Windows implementations
# ---------------------------------------------------------------------------

def _find_window_windows(title_substring: str) -> Optional[str]:
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(title_substring)
        if windows:
            return str(windows[0]._hWnd)
    except ImportError:
        pass

    # Fallback: use ctypes
    try:
        import ctypes
        import ctypes.wintypes

        result = []
        EnumWindowsProc = ctypes.WINFUNCTYPE(
            ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM
        )

        def callback(hwnd, _lparam):
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                if title_substring.lower() in buf.value.lower():
                    result.append(str(hwnd))
            return True

        ctypes.windll.user32.EnumWindows(EnumWindowsProc(callback), 0)
        return result[0] if result else None
    except Exception:
        return None


def _focus_window_windows(window_id: str) -> bool:
    try:
        import pygetwindow as gw
        for win in gw.getAllWindows():
            if str(win._hWnd) == window_id:
                if win.isMinimized:
                    win.restore()
                win.activate()
                time.sleep(0.3)
                return True
    except ImportError:
        pass

    try:
        import ctypes
        hwnd = int(window_id)
        ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        time.sleep(0.3)
        return True
    except Exception:
        return False


def _list_windows_windows(title_filter: Optional[str]) -> List[str]:
    results = []
    try:
        import pygetwindow as gw
        for win in gw.getAllWindows():
            if win.title:
                if title_filter is None or title_filter.lower() in win.title.lower():
                    results.append(win.title)
    except ImportError:
        pass
    return results


def _get_window_text_windows(window_id: str) -> Optional[str]:
    """Read the console screen buffer text (Windows only)."""
    try:
        import ctypes
        import ctypes.wintypes

        STD_OUTPUT_HANDLE = -11
        handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

        class COORD(ctypes.Structure):
            _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

        class SMALL_RECT(ctypes.Structure):
            _fields_ = [
                ("Left", ctypes.c_short),
                ("Top", ctypes.c_short),
                ("Right", ctypes.c_short),
                ("Bottom", ctypes.c_short),
            ]

        class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
            _fields_ = [
                ("dwSize", COORD),
                ("dwCursorPosition", COORD),
                ("wAttributes", ctypes.wintypes.WORD),
                ("srWindow", SMALL_RECT),
                ("dwMaximumWindowSize", COORD),
            ]

        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        ctypes.windll.kernel32.GetConsoleScreenBufferInfo(handle, ctypes.byref(csbi))
        cols = csbi.dwSize.X
        rows = csbi.dwSize.Y

        # Read the last 40 rows (most recent output)
        start_row = max(0, csbi.dwCursorPosition.Y - 40)
        num_rows = csbi.dwCursorPosition.Y - start_row + 1
        total_chars = cols * num_rows

        buf = ctypes.create_unicode_buffer(total_chars)
        read = ctypes.wintypes.DWORD()
        coord = COORD(0, start_row)
        ctypes.windll.kernel32.ReadConsoleOutputCharacterW(
            handle, buf, total_chars, coord, ctypes.byref(read)
        )

        text = buf.value
        lines = [text[i : i + cols].rstrip() for i in range(0, len(text), cols)]
        return "\n".join(lines)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Linux implementations
# ---------------------------------------------------------------------------

def _find_window_linux(title_substring: str) -> Optional[str]:
    try:
        output = subprocess.check_output(
            ["wmctrl", "-l"], stderr=subprocess.DEVNULL, text=True
        )
        for line in output.strip().splitlines():
            parts = line.split(None, 3)
            if len(parts) >= 4 and title_substring.lower() in parts[3].lower():
                return parts[0]
    except FileNotFoundError:
        pass

    # Fallback to xdotool
    try:
        output = subprocess.check_output(
            ["xdotool", "search", "--name", title_substring],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        ids = output.strip().splitlines()
        return ids[0] if ids else None
    except FileNotFoundError:
        return None


def _focus_window_linux(window_id: str) -> bool:
    try:
        subprocess.check_call(
            ["wmctrl", "-i", "-a", window_id], stderr=subprocess.DEVNULL
        )
        time.sleep(0.3)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    try:
        subprocess.check_call(
            ["xdotool", "windowactivate", window_id], stderr=subprocess.DEVNULL
        )
        time.sleep(0.3)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _list_windows_linux(title_filter: Optional[str]) -> List[str]:
    results = []
    try:
        output = subprocess.check_output(
            ["wmctrl", "-l"], stderr=subprocess.DEVNULL, text=True
        )
        for line in output.strip().splitlines():
            parts = line.split(None, 3)
            if len(parts) >= 4:
                title = parts[3]
                if title_filter is None or title_filter.lower() in title.lower():
                    results.append(title)
    except FileNotFoundError:
        pass
    return results


# ---------------------------------------------------------------------------
# macOS implementations
# ---------------------------------------------------------------------------

def _find_window_macos(title_substring: str) -> Optional[str]:
    script = f'''
    tell application "System Events"
        set matchedWindows to {{}}
        repeat with proc in (every process whose background only is false)
            repeat with win in (every window of proc)
                if name of win contains "{title_substring}" then
                    return name of win
                end if
            end repeat
        end repeat
    end tell
    return ""
    '''
    try:
        result = subprocess.check_output(
            ["osascript", "-e", script], stderr=subprocess.DEVNULL, text=True
        ).strip()
        return result if result else None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _focus_window_macos(window_id: str) -> bool:
    # window_id is the window name on macOS
    script = f'''
    tell application "System Events"
        repeat with proc in (every process whose background only is false)
            repeat with win in (every window of proc)
                if name of win is "{window_id}" then
                    set frontmost of proc to true
                    return true
                end if
            end repeat
        end repeat
    end tell
    return false
    '''
    try:
        subprocess.check_call(
            ["osascript", "-e", script], stderr=subprocess.DEVNULL
        )
        time.sleep(0.3)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _list_windows_macos(title_filter: Optional[str]) -> List[str]:
    script = '''
    set output to ""
    tell application "System Events"
        repeat with proc in (every process whose background only is false)
            repeat with win in (every window of proc)
                set output to output & name of win & linefeed
            end repeat
        end repeat
    end tell
    return output
    '''
    try:
        result = subprocess.check_output(
            ["osascript", "-e", script], stderr=subprocess.DEVNULL, text=True
        ).strip()
        titles = [t for t in result.splitlines() if t.strip()]
        if title_filter:
            titles = [t for t in titles if title_filter.lower() in t.lower()]
        return titles
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
