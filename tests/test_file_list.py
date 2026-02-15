"""Tests for src.file_list."""

import pytest

from src.file_list import parse_file_list


class TestParseFileList:
    def test_comma_separated(self):
        result = parse_file_list("batch_001.txt,batch_002.txt,batch_003.txt")
        assert result == ["batch_001.txt", "batch_002.txt", "batch_003.txt"]

    def test_with_whitespace(self):
        result = parse_file_list(" batch_001.txt , batch_002.txt ")
        assert result == ["batch_001.txt", "batch_002.txt"]

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="empty"):
            parse_file_list("")

    def test_single_file(self):
        result = parse_file_list("only_one.txt")
        assert result == ["only_one.txt"]
