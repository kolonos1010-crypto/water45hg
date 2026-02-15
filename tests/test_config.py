"""Tests for src.config."""

import os
import tempfile

import pytest

from src.config import Config


def _write_notes(content: str) -> str:
    """Write a temp notes file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "w") as fh:
        fh.write(content)
    return path


class TestConfig:
    def test_parse_valid_notes(self):
        path = _write_notes(
            "MODULE: 1\nAPI_KEYS: key_aaa,key_bbb,key_ccc\n"
        )
        cfg = Config.from_file(path)
        assert cfg.module == 1
        assert cfg.api_keys == ["key_aaa", "key_bbb", "key_ccc"]
        os.unlink(path)

    def test_parse_with_comments_and_blanks(self):
        path = _write_notes(
            "# comment\n\nMODULE: 2\n\nAPI_KEYS: k1,k2\n"
        )
        cfg = Config.from_file(path)
        assert cfg.module == 2
        assert cfg.api_keys == ["k1", "k2"]
        os.unlink(path)

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            Config.from_file("/tmp/nonexistent_notes_abc123.txt")

    def test_no_keys_raises(self):
        path = _write_notes("MODULE: 1\n")
        with pytest.raises(ValueError, match="No API keys"):
            Config.from_file(path)
        os.unlink(path)

    def test_rotate_key(self):
        cfg = Config(api_keys=["a", "b", "c"])
        drained = cfg.rotate_key()
        assert drained == "a"
        assert cfg.api_keys == ["b", "c"]

    def test_rotate_single_key_raises(self):
        cfg = Config(api_keys=["only"])
        with pytest.raises(ValueError, match="No more API keys"):
            cfg.rotate_key()
