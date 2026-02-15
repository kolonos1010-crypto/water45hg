"""Runner: orchestrates per-file processing loop with console interaction."""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Callable

from src.config import Config
from src.console_monitor import (
    CaptureResult,
    LoadedResult,
    TriggerType,
    monitor_for_loaded,
    detect_trigger,
)

logger = logging.getLogger(__name__)


@dataclass
class FileResult:
    """Outcome of processing a single file."""
    filename: str
    bot_count: Optional[int] = None
    duplicates_removed: Optional[int] = None
    status: str = "PENDING"  # COMPLETED, ERROR, SKIPPED
    trigger: Optional[TriggerType] = None
    details: str = ""
    api_key_used: str = ""


@dataclass
class BatchState:
    """Accumulated state across an entire batch run."""
    config: Config
    files: List[str]
    results: List[FileResult] = field(default_factory=list)
    current_key_index: int = 0
    key_usage: dict = field(default_factory=dict)  # key -> list of FileResult

    @property
    def current_key(self) -> str:
        return self.config.api_keys[self.current_key_index]

    def rotate_key(self) -> bool:
        """Advance to the next key. Returns False if no keys remain."""
        if self.current_key_index + 1 < len(self.config.api_keys):
            self.current_key_index += 1
            return True
        return False


def format_file_select_log(filename: str) -> str:
    return f"\U0001f4c1 SELECTING: {filename}"


def format_capture_log(filename: str, result: LoadedResult) -> str:
    return (
        f"\U0001f440 REAL-TIME CAPTURE: {filename}\n"
        f"\u2192 LOADED: {result.loaded} (unique numbers)\n"
        f"\u2192 DUPLICATES REMOVED: {result.duplicates_removed}\n"
        f"\u2192 BOT COUNT SET TO: {result.loaded}\n"
        f"(Captured from console output)"
    )


def format_capture_failure(filename: str) -> str:
    return (
        f"\u26a0\ufe0f CRITICAL: LOADED NUMBER NOT DETECTED. "
        f"ABORTING FILE. [PRESS ENTER TO CONTINUE]"
    )


def format_pause_trigger(
    trigger: TriggerType,
    filename: str,
    bot_count: Optional[int],
    status: str,
    details: str,
) -> str:
    action = "SWITCH KEY" if trigger in (
        TriggerType.API_USAGE_EXCEEDED,
        TriggerType.RATE_LIMIT,
        TriggerType.INVALID_KEY,
    ) else "REVIEW"
    bc = str(bot_count) if bot_count is not None else "N/A"
    return (
        f"\u26a0\ufe0f PAUSE TRIGGER: {trigger.value}\n"
        f"\u2501" * 40 + "\n"
        f"File: {filename}\n"
        f"Bot Count: {bc}\n"
        f"Status: {status}\n"
        f"Details: {details}\n"
        f"Action: {action}\n"
        f"[PRESS ENTER TO CONTINUE]"
    )


def process_file(
    filename: str,
    state: BatchState,
    read_line: Callable[[], Optional[str]],
    send_input: Callable[[str], None],
    log_fn: Callable[[str], None] = logger.info,
    capture_timeout: float = 3.0,
) -> FileResult:
    """Process a single file through the console automation workflow.

    Args:
        filename: Name of the .txt number file to process.
        state: Current batch state (for key tracking).
        read_line: Callable returning next console line or None.
        send_input: Callable to send text input to the console process.
        log_fn: Logging function for status output.
        capture_timeout: Seconds to wait for the Loaded pattern.

    Returns:
        FileResult with outcome details.
    """
    result = FileResult(filename=filename, api_key_used=state.current_key)

    # Step 2.1 - File selection
    log_fn(format_file_select_log(filename))
    send_input("")  # Press Enter to select file

    # Step 2.2 - Real-time console monitoring
    capture = monitor_for_loaded(read_line, timeout_seconds=capture_timeout)

    if not capture.success:
        log_fn(format_capture_failure(filename))
        result.status = "SKIPPED"
        result.details = "Loaded number not captured (3s timeout)"
        return result

    loaded = capture.loaded_result
    result.bot_count = loaded.loaded
    result.duplicates_removed = loaded.duplicates_removed
    log_fn(format_capture_log(filename, loaded))

    # Step 2.3 - Dynamic bot execution
    send_input(str(loaded.loaded))

    # Monitor for triggers
    while True:
        line = read_line()
        if line is None:
            continue
        trigger = detect_trigger(line)
        if trigger:
            result.trigger = trigger
            if trigger == TriggerType.TASK_COMPLETED:
                result.status = "COMPLETED"
                result.details = line.strip()
            else:
                result.status = "ERROR"
                result.details = line.strip()

            log_fn(
                format_pause_trigger(
                    trigger, filename, result.bot_count, result.status, result.details
                )
            )
            break

    # Track key usage
    key = state.current_key
    state.key_usage.setdefault(key, []).append(result)

    # Rotate key on API errors
    if result.trigger in (
        TriggerType.API_USAGE_EXCEEDED,
        TriggerType.RATE_LIMIT,
        TriggerType.INVALID_KEY,
    ):
        if not state.rotate_key():
            log_fn("\u26a0\ufe0f ALL API KEYS EXHAUSTED")

    state.results.append(result)
    return result


def run_batch(
    state: BatchState,
    read_line: Callable[[], Optional[str]],
    send_input: Callable[[str], None],
    log_fn: Callable[[str], None] = logger.info,
) -> List[FileResult]:
    """Run the full batch of files."""
    for filename in state.files:
        process_file(filename, state, read_line, send_input, log_fn)
    return state.results
