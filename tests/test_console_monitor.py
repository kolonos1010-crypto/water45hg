"""Tests for src.console_monitor."""

import time
from typing import List, Optional

import pytest

from src.console_monitor import (
    CaptureResult,
    LoadedResult,
    TriggerType,
    detect_trigger,
    is_bot_prompt,
    is_file_prompt,
    monitor_for_loaded,
    parse_loaded_line,
)


class TestParseLoadedLine:
    def test_standard_format(self):
        result = parse_loaded_line("Loaded 94950 | Removed 50 duplicates")
        assert result is not None
        assert result.loaded == 94950
        assert result.duplicates_removed == 50

    def test_with_extra_whitespace(self):
        result = parse_loaded_line("  Loaded  12345  |  Removed  5  duplicates  ")
        assert result is not None
        assert result.loaded == 12345
        assert result.duplicates_removed == 5

    def test_case_insensitive(self):
        result = parse_loaded_line("loaded 100 | removed 10 DUPLICATES")
        assert result is not None
        assert result.loaded == 100

    def test_no_match(self):
        assert parse_loaded_line("some other output") is None

    def test_partial_match(self):
        assert parse_loaded_line("Loaded 100") is None


class TestDetectTrigger:
    def test_api_usage_exceeded(self):
        assert detect_trigger("API usage exceeded for key abc") == TriggerType.API_USAGE_EXCEEDED

    def test_rate_limit(self):
        assert detect_trigger("Rate limit hit, waiting...") == TriggerType.RATE_LIMIT

    def test_invalid_key(self):
        assert detect_trigger("Invalid key provided") == TriggerType.INVALID_KEY

    def test_task_completed(self):
        assert detect_trigger("Task completed successfully") == TriggerType.TASK_COMPLETED

    def test_no_trigger(self):
        assert detect_trigger("Processing file batch_001.txt") is None


class TestPromptDetection:
    def test_file_prompt(self):
        assert is_file_prompt("Press Enter to open your Numbers file :")
        assert not is_file_prompt("some other text")

    def test_bot_prompt(self):
        assert is_bot_prompt("How many bots :")
        assert not is_bot_prompt("some other text")


class TestMonitorForLoaded:
    def test_immediate_capture(self):
        lines = ["Loaded 500 | Removed 10 duplicates"]
        idx = [0]

        def read_line() -> Optional[str]:
            if idx[0] < len(lines):
                line = lines[idx[0]]
                idx[0] += 1
                return line
            return None

        result = monitor_for_loaded(read_line, timeout_seconds=1.0)
        assert result.success is True
        assert result.loaded_result.loaded == 500
        assert result.loaded_result.duplicates_removed == 10

    def test_timeout_no_loaded(self):
        def read_line() -> Optional[str]:
            return None

        result = monitor_for_loaded(read_line, timeout_seconds=0.3)
        assert result.success is False
        assert "CRITICAL" in result.error_message

    def test_loaded_after_noise(self):
        lines = [
            "Starting process...",
            "Reading file...",
            "Loaded 1000 | Removed 25 duplicates",
        ]
        idx = [0]

        def read_line() -> Optional[str]:
            if idx[0] < len(lines):
                line = lines[idx[0]]
                idx[0] += 1
                return line
            return None

        result = monitor_for_loaded(read_line, timeout_seconds=2.0)
        assert result.success is True
        assert result.loaded_result.loaded == 1000
