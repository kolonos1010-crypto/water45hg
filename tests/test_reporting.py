"""Tests for src.reporting."""

from src.config import Config
from src.console_monitor import TriggerType
from src.reporting import build_report
from src.runner import BatchState, FileResult


class TestBuildReport:
    def _make_state(self, results, keys=None):
        keys = keys or ["key_aaaa1111", "key_bbbb2222"]
        config = Config(api_keys=list(keys))
        state = BatchState(config=config, files=[r.filename for r in results])
        state.results = results
        for r in results:
            state.key_usage.setdefault(r.api_key_used, []).append(r)
        return state

    def test_all_success(self):
        results = [
            FileResult(
                filename="batch_001.txt",
                bot_count=1000,
                duplicates_removed=10,
                status="COMPLETED",
                trigger=TriggerType.TASK_COMPLETED,
                api_key_used="key_aaaa1111",
            ),
        ]
        report = build_report(self._make_state(results))
        assert "ALL SUCCESS" in report
        assert "BATCH VALIDATION COMPLETE" in report
        assert "Files Processed: 1" in report
        assert "[None]" in report

    def test_partial_success_with_errors(self):
        results = [
            FileResult(
                filename="batch_001.txt",
                bot_count=500,
                duplicates_removed=5,
                status="COMPLETED",
                trigger=TriggerType.TASK_COMPLETED,
                api_key_used="key_aaaa1111",
            ),
            FileResult(
                filename="batch_002.txt",
                bot_count=None,
                duplicates_removed=None,
                status="SKIPPED",
                api_key_used="key_aaaa1111",
            ),
        ]
        report = build_report(self._make_state(results))
        assert "PARTIAL SUCCESS" in report
        assert "LOADED NUMBER NOT CAPTURED" in report

    def test_key_drained(self):
        results = [
            FileResult(
                filename="batch_001.txt",
                bot_count=100,
                duplicates_removed=2,
                status="ERROR",
                trigger=TriggerType.API_USAGE_EXCEEDED,
                api_key_used="key_aaaa1111",
            ),
        ]
        report = build_report(self._make_state(results))
        assert "DRAINED" in report
