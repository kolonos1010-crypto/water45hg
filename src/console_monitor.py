"""Console monitor: watches stdout for patterns and extracts data."""

import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable, List


class TriggerType(Enum):
    API_USAGE_EXCEEDED = "API usage exceeded"
    RATE_LIMIT = "Rate limit"
    INVALID_KEY = "Invalid key"
    TASK_COMPLETED = "Task completed"


@dataclass
class LoadedResult:
    """Result of parsing a 'Loaded [X] | Removed [Y] duplicates' line."""
    loaded: int
    duplicates_removed: int


@dataclass
class CaptureResult:
    """Result of a real-time capture attempt."""
    success: bool
    loaded_result: Optional[LoadedResult] = None
    error_message: Optional[str] = None


# Regex for: Loaded [X] | Removed [Y] duplicates
LOADED_PATTERN = re.compile(
    r"Loaded\s+(\d+)\s*\|\s*Removed\s+(\d+)\s+duplicates",
    re.IGNORECASE,
)

# Trigger patterns
TRIGGER_PATTERNS = {
    TriggerType.API_USAGE_EXCEEDED: re.compile(r"API usage exceeded", re.IGNORECASE),
    TriggerType.RATE_LIMIT: re.compile(r"Rate limit", re.IGNORECASE),
    TriggerType.INVALID_KEY: re.compile(r"Invalid key", re.IGNORECASE),
    TriggerType.TASK_COMPLETED: re.compile(r"Task completed", re.IGNORECASE),
}

# Prompt patterns
FILE_PROMPT_PATTERN = re.compile(
    r"Press Enter to open your Numbers file\s*:", re.IGNORECASE
)
BOT_PROMPT_PATTERN = re.compile(r"How many bots\s*:", re.IGNORECASE)


def parse_loaded_line(line: str) -> Optional[LoadedResult]:
    """Parse a console line for the Loaded [X] | Removed [Y] duplicates pattern."""
    match = LOADED_PATTERN.search(line)
    if match:
        return LoadedResult(
            loaded=int(match.group(1)),
            duplicates_removed=int(match.group(2)),
        )
    return None


def detect_trigger(line: str) -> Optional[TriggerType]:
    """Check if a console line contains any known trigger."""
    for trigger_type, pattern in TRIGGER_PATTERNS.items():
        if pattern.search(line):
            return trigger_type
    return None


def is_file_prompt(line: str) -> bool:
    """Check if console output is the file selection prompt."""
    return bool(FILE_PROMPT_PATTERN.search(line))


def is_bot_prompt(line: str) -> bool:
    """Check if console output is the bot count prompt."""
    return bool(BOT_PROMPT_PATTERN.search(line))


def monitor_for_loaded(
    read_line: Callable[[], Optional[str]],
    timeout_seconds: float = 3.0,
    poll_interval: float = 0.1,
) -> CaptureResult:
    """Watch console output for up to `timeout_seconds` for the Loaded pattern.

    Args:
        read_line: Callable that returns the next console line or None if no
                   new output is available.
        timeout_seconds: Maximum time to wait for the pattern.
        poll_interval: Time between read attempts.

    Returns:
        CaptureResult with success=True and data if found, or success=False
        with an error message if the timeout elapses.
    """
    deadline = time.monotonic() + timeout_seconds
    lines_seen: List[str] = []

    while time.monotonic() < deadline:
        line = read_line()
        if line is not None:
            lines_seen.append(line)
            result = parse_loaded_line(line)
            if result:
                return CaptureResult(success=True, loaded_result=result)
        else:
            time.sleep(poll_interval)

    return CaptureResult(
        success=False,
        error_message=(
            "CRITICAL: LOADED NUMBER NOT DETECTED. ABORTING FILE. "
            "[PRESS ENTER TO CONTINUE]"
        ),
    )


def monitor_for_triggers(
    read_line: Callable[[], Optional[str]],
    poll_interval: float = 0.1,
) -> Optional[TriggerType]:
    """Continuously read lines and return the first trigger detected.

    This is a blocking call; the caller should run it in a thread or
    use a non-blocking `read_line` with its own exit condition.
    """
    while True:
        line = read_line()
        if line is not None:
            trigger = detect_trigger(line)
            if trigger:
                return trigger
        else:
            time.sleep(poll_interval)
