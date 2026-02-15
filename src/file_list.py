"""File list parser: reads a comma-separated list of .txt filenames."""

from typing import List


def parse_file_list(raw: str) -> List[str]:
    """Parse a comma-separated string of filenames into a list.

    Args:
        raw: e.g. "batch_001.txt,batch_002.txt,batch_003.txt"

    Returns:
        List of stripped, non-empty filenames.
    """
    files = [f.strip() for f in raw.split(",") if f.strip()]
    if not files:
        raise ValueError("File list is empty")
    return files


def load_file_list(path: str) -> List[str]:
    """Load file list from a text file (one filename per line or comma-separated)."""
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read().strip()

    # Support both comma-separated and newline-separated
    if "," in content:
        return parse_file_list(content)
    else:
        files = [line.strip() for line in content.splitlines() if line.strip()]
        if not files:
            raise ValueError("File list is empty")
        return files
