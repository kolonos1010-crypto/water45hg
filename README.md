# Console Monitoring Automation Engine

Autonomous console monitoring agent that watches terminal output for patterns, extracts data in real-time, and orchestrates batch processing with API key rotation and comprehensive reporting.

## What It Does

- Monitors console output for `Loaded [X] | Removed [Y] duplicates` patterns
- Extracts loaded count as `bot_count` and inputs it when `How many bots :` appears
- Processes a queue of `.txt` number files automatically
- Detects pause triggers: API usage exceeded, Rate limit, Invalid key, Task completed
- Rotates API keys on failures
- Produces a final batch validation report with metrics, key usage, and error audit

## Project Structure

```
src/
  config.py           - Reads notes.txt (MODULE, API_KEYS)
  file_list.py        - Parses comma-separated file lists
  console_monitor.py  - Real-time console pattern matching and trigger detection
  runner.py           - Per-file processing loop with console interaction
  reporting.py        - Final batch report builder
  main.py             - CLI entry point
tests/
  test_config.py
  test_console_monitor.py
  test_file_list.py
  test_reporting.py
data/
  batch_001.txt       - Sample number files
  batch_002.txt
  batch_003.txt
docs/
  controller_prompt.md - Full controller prompt for Claude Code infinity loop
graph.py              - LangGraph agent graph for autonomous dev loop
notes.txt             - Configuration (MODULE + API_KEYS)
requirements.txt      - Python dependencies
```

## Setup

```bash
python -m venv .venv
# Linux/Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

## Running Tests

```bash
python -m pytest
```

## Usage

### Direct CLI

```bash
python -m src.main \
  --notes notes.txt \
  --files "batch_001.txt,batch_002.txt,batch_003.txt" \
  --command "your_console_app_here"
```

### LangGraph Agent (Infinity Loop)

The `graph.py` file implements an autonomous dev+ops loop using LangGraph:

```bash
python graph.py
```

This runs Claude through repeated cycles of:
1. **NEXT_TASK** - Identify highest-value improvement
2. **PLAN** - Design implementation steps
3. **IMPLEMENT** - Edit/create files via tools
4. **TEST & SELF_EVAL** - Run tests, evaluate, decide next iteration

The agent has access to tools: `read_file`, `write_file`, `list_files`, `run_shell`.

### Controller Prompt (Manual)

See `docs/controller_prompt.md` for the full prompt to paste into Claude Code for manual operation.

## Configuration

`notes.txt` format:
```
MODULE: 1
API_KEYS: key1,key2,key3
```

File list: comma-separated `.txt` filenames, each containing one number per line.

## Console Patterns

| Pattern | Action |
|---|---|
| `Press Enter to open your Numbers file :` | Auto-select next file |
| `Loaded [X] \| Removed [Y] duplicates` | Extract X as bot_count (3s timeout) |
| `How many bots :` | Input captured bot_count |
| `API usage exceeded` / `Rate limit` / `Invalid key` | Pause, rotate key |
| `Task completed` | Mark file complete, proceed |
