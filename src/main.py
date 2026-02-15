"""Entry point for the Console Monitoring Automation Engine."""

import argparse
import logging
import subprocess
import sys
import threading
import queue
from typing import Optional

from src.config import Config
from src.file_list import parse_file_list
from src.runner import BatchState, run_batch
from src.reporting import build_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def create_console_reader(proc: subprocess.Popen, output_queue: queue.Queue):
    """Background thread that reads process stdout and enqueues lines."""
    def _reader():
        assert proc.stdout is not None
        for raw_line in iter(proc.stdout.readline, ""):
            line = raw_line.rstrip("\n\r")
            if line:
                output_queue.put(line)
                logger.info(f"[CONSOLE] {line}")
        output_queue.put(None)  # Sentinel
    return _reader


def main():
    parser = argparse.ArgumentParser(
        description="Console Monitoring Automation Engine"
    )
    parser.add_argument(
        "--notes", default="notes.txt", help="Path to notes.txt config file"
    )
    parser.add_argument(
        "--files",
        required=True,
        help="Comma-separated list of .txt number files",
    )
    parser.add_argument(
        "--command",
        required=True,
        help="Console command to launch and monitor",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=3.0,
        help="Seconds to wait for Loaded pattern (default: 3)",
    )
    args = parser.parse_args()

    # Load config
    config = Config.from_file(args.notes)
    logger.info(f"Module: {config.module}")
    logger.info(f"API Keys loaded: {len(config.api_keys)}")

    # Parse file list
    files = parse_file_list(args.files)
    logger.info(f"Files to process: {files}")

    # Launch target console process
    proc = subprocess.Popen(
        args.command,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    output_queue: queue.Queue = queue.Queue()
    reader_thread = threading.Thread(
        target=create_console_reader(proc, output_queue),
        daemon=True,
    )
    reader_thread.start()

    def read_line() -> Optional[str]:
        try:
            return output_queue.get(timeout=0.1)
        except queue.Empty:
            return None

    def send_input(text: str) -> None:
        assert proc.stdin is not None
        proc.stdin.write(text + "\n")
        proc.stdin.flush()

    # Run batch
    state = BatchState(config=config, files=files)
    run_batch(state, read_line, send_input, log_fn=logger.info)

    # Final report
    report = build_report(state)
    print(report)

    # Cleanup
    proc.terminate()
    proc.wait(timeout=5)


if __name__ == "__main__":
    main()
