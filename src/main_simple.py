"""Simplified Entry Point - Just Point to a Folder!"""

import argparse
import logging
import subprocess
import sys
import threading
import queue
from pathlib import Path
from typing import Optional

from src.config import Config
from src.runner import BatchState, run_batch
from src.reporting import build_report

logging.basicConfig(
          level=logging.INFO,
          format="%(asctime)s | %(message)s",
          datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)


def find_api_config(folder: Path) -> Path:
          """Find API configuration file in folder."""
          # Look for API_CONFIGURATION.txt first
    config_file = folder / "API_CONFIGURATION.txt"
    if config_file.exists():
                  return config_file
              
    # Fall back to notes.txt
    config_file = folder / "notes.txt"
    if config_file.exists():
                  return config_file
              
    raise FileNotFoundError(f"No API_CONFIGURATION.txt or notes.txt found in {folder}")


def find_number_files(folder: Path) -> list:
          """Find all .txt number files in folder (excluding config files)."""
          files = []
          for txt_file in sorted(folder.glob("*.txt")):
                        # Skip config files
                        if txt_file.name in ["API_CONFIGURATION.txt", "notes.txt"]:
                                          continue
                                      files.append(txt_file.name)
                    
          if not files:
                        raise FileNotFoundError(f"No number files (.txt) found in {folder}")
                    
          return files
      

def create_console_reader(proc: subprocess.Popen, output_queue: queue.Queue):
          """Background thread that reads process stdout and enqueues lines."""
          assert proc.stdout is not None
          
          for raw_line in iter(proc.stdout.readline, ""):
                        line = raw_line.rstrip("\n\r")
                        if line:
                                          output_queue.put(line)
                                          logger.info(f"[CONSOLE] {line}")
                                  
                    output_queue.put(None)  # Sentinel


def main():
          """Simplified main - just point to a folder!"""
    parser = argparse.ArgumentParser(
                  description="Console Monitoring Automation Engine - SIMPLE MODE"
    )
    
    parser.add_argument(
                  "--folder",
                  required=True,
                  help="Folder containing API_CONFIGURATION.txt and .txt number files"
    )
    
    parser.add_argument(
                  "--command",
                  required=True,
                  help="Console command to launch and monitor"
    )
    
    parser.add_argument(
                  "--timeout",
                  type=float,
                  default=3.0,
                  help="Seconds to wait for Loaded pattern (default: 3)"
    )
    
    args = parser.parse_args()
    
    # Convert folder path to Path object
    folder = Path(args.folder)
    if not folder.exists():
                  logger.error(f"Folder not found: {folder}")
                  sys.exit(1)
              
    # Find API config and number files automatically
    logger.info(f"Looking in folder: {folder}")
    
    try:
                  api_config_file = find_api_config(folder)
                  logger.info(f"Found API config: {api_config_file.name}")
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    
    try:
                  number_files = find_number_files(folder)
                  logger.info(f"Found {len(number_files)} number files to process: {number_files}")
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    
    # Load config
    config = Config.from_file(str(api_config_file))
    logger.info(f"Module: {config.module}")
    logger.info(f"API Keys loaded: {len(config.api_keys)}")
    
    # Launch target console process
    logger.info(f"Launching: {args.command}")
    proc = subprocess.Popen(
                  args.command,
                  shell=True,
                  stdin=subprocess.PIPE,
                  stdout=subprocess.PIPE,
                  stderr=subprocess.STDOUT,
                  text=True,
                  bufsize=1,
                  cwd=folder,
    )
    
    output_queue = queue.Queue()
    reader_thread = threading.Thread(
                  target=create_console_reader,
                  args=(proc, output_queue),
                  daemon=True,
    )
    reader_thread.start()
    
    def read_line() -> Optional[str]:
                  """Read next console line or None if no new output."""
                  try:
                                    return output_queue.get(timeout=0.1)
                  except queue.Empty:
                                    return None
                            
              def send_input(text: str) -> None:
                            """Send text input to the console process."""
                            assert proc.stdin is not None
                            proc.stdin.write(text + "\n")
                            proc.stdin.flush()
                        
    # Run batch processing
    state = BatchState(config=config, files=number_files)
    run_batch(state, read_line, send_input, log_fn=logger.info)
    
    # Final report
    report = build_report(state)
    print(report)
    
    # Cleanup
    proc.terminate()
    try:
                  proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


if __name__ == "__main__":
          main()
"""Simplified Entry Point - Just Point to a Folder!"""

import argparse
import logging
import subprocess
import sys
import threading
import queue
import os
from pathlib import Path
from typing import Optional

from src.config import Config
from src.runner import BatchState, run_batch
from src.reporting import build_report

logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s | %(message)s",
      datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)


def find_api_config(folder: Path) -> Path:
      """Find API configuration file in folder."""
      # Look for API_CONFIGURATION.txt first
      config_file = folder / "API_CONFIGURATION.txt"
      if config_file.exists():
                return config_file

      # Fall back to notes.txt
      config_file = folder / "notes.txt"
      if config_file.exists():
                return config_file

      raise FileNotFoundError(f"No API_CONFIGURATION.txt or notes.txt found in {folder}")


def find_number_files(folder: Path) -> list:
      """Find all .txt number files in folder (excluding config files)."""
      files = []
      for txt_file in sorted(folder.glob("*.txt")):
                # Skip config files
                if txt_file.name in ["API_CONFIGURATION.txt", "notes.txt"]:
                              continue
                          files.append(txt_file.name)

      if not files:
                raise FileNotFoundError(f"No number files (.txt) found in {folder}")

      return files


def create_console_reader(proc: subprocess.Popen, output_queue: queue.Queue):
      """Background thread that reads process stdout and enqueues lines."""
      assert proc.stdout is not None

    for raw_line in iter(proc.stdout.readline, ""):
              line = raw_line.rstrip("\n\r")
              if line:
                            output_queue.put(line)
                        logger.info(f"[CONSOLE] {line}")

    output_queue.put(None)  # Sentinel


def read_line() -> Optional[str]:
      """Read next console line or None if no new output."""
    try:
              return output_queue.get(timeout=0.1)
except queue.Empty:
        return None


def send_input(text: str) -> None:
      """Send text input to the console process."""
    assert proc.stdin is not None
    proc.stdin.write(text + "\n")
    proc.stdin.flush()


def main():
      """Simplified main - just point to a folder!"""
    parser = argparse.ArgumentParser(
        description="Console Monitoring Automation Engine - SIMPLE MODE"
    )

    parser.add_argument(
        "--folder",
              required=True,
              help="Folder containing API_CONFIGURATION.txt and .txt number files"
    )

    parser.add_argument(
              "--command",
              required=True,
              help="Console command to launch and monitor"
    )

    parser.add_argument(
              "--timeout",
              type=float,
              default=3.0,
              help="Seconds to wait for Loaded pattern (default: 3)"
    )

    args = parser.parse_args()

    # Convert folder path to Path object
    folder = Path(args.folder)
    if not folder.exists():
              logger.error(f"Folder not found: {folder}")
        sys.exit(1)

    # Find API config and number files automatically
    logger.info(f"Looking in folder: {folder}")

    try:
              api_config_file = find_api_config(folder)
        logger.info(f"Found API config: {api_config_file.name}")
except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

    try:
        number_files = find_number_files(folder)
        logger.info(f"Found {len(number_files)} number files to process: {number_files}")
except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

    # Load config
    config = Config.from_file(str(api_config_file))
    logger.info(f"Module: {config.module}")
    logger.info(f"API Keys loaded: {len(config.api_keys)}")

    # Launch target console process
    logger.info(f"Launching: {args.command}")
    proc = subprocess.Popen(
              args.command,
              shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
              stderr=subprocess.STDOUT,
              text=True,
              bufsize=1,
              cwd=folder,
)

    output_queue = queue.Queue()
    reader_thread = threading.Thread(
        target=create_console_reader,
              args=(proc, output_queue),
              daemon=True,
    )
    reader_thread.start()

    # Run batch processing
    state = BatchState(config=config, files=number_files)
    run_batch(state, read_line, send_input, log_fn=logger.info)

    # Final report
    report = build_report(state)
    print(report)

    # Cleanup
    proc.terminate()
    proc.wait(timeout=5)


if __name__ == "__main__":
      main()
