"""Reporting: builds the final batch validation report."""

from typing import List, Dict

from src.runner import BatchState, FileResult
from src.console_monitor import TriggerType


def _mask_key(key: str) -> str:
    """Show first 8 chars of a key followed by '...'."""
    if len(key) <= 8:
        return key
    return key[:8] + "..."


def build_report(state: BatchState) -> str:
    """Generate the final batch validation report.

    Args:
        state: The completed BatchState with all results.

    Returns:
        Formatted report string matching the specification.
    """
    results = state.results
    total_files = len(results)
    total_numbers = sum(r.bot_count or 0 for r in results)
    unique_numbers = total_numbers  # Loaded count = unique
    total_duplicates = sum(r.duplicates_removed or 0 for r in results)

    # Determine final status
    errors = [r for r in results if r.status == "ERROR"]
    skipped = [r for r in results if r.status == "SKIPPED"]
    completed = [r for r in results if r.status == "COMPLETED"]

    if not errors and not skipped:
        final_status = "ALL SUCCESS"
    elif completed:
        final_status = "PARTIAL SUCCESS"
    else:
        final_status = "FAILED"

    lines = [
        "",
        "\u2705\u2705\u2705 BATCH VALIDATION COMPLETE \u2705\u2705\u2705",
        "\u2501" * 40,
        "REAL-TIME METRICS",
        "\u2501" * 40,
        f"Files Processed: {total_files}",
        f"Total Numbers Validated: {total_numbers}",
        f"Unique Numbers (from console): {unique_numbers}",
        f"Duplicates Removed: {total_duplicates}",
        "",
        "API KEY ROTATION LOG",
        "\u2501" * 40,
    ]

    # Key usage summary
    all_keys = state.config.api_keys
    # Include keys that were rotated out (tracked in key_usage)
    reported_keys: set = set()
    key_index = 0
    for key in list(state.key_usage.keys()) + all_keys:
        if key in reported_keys:
            continue
        reported_keys.add(key)
        key_index += 1
        usage = state.key_usage.get(key, [])
        file_count = len(usage)
        loaded_total = sum(r.bot_count or 0 for r in usage)
        drained = any(
            r.trigger in (
                TriggerType.API_USAGE_EXCEEDED,
                TriggerType.RATE_LIMIT,
                TriggerType.INVALID_KEY,
            )
            for r in usage
        )
        if drained:
            lines.append(
                f"\u2717 Key #{key_index}: {_mask_key(key)} "
                f"\u2192 DRAINED after {file_count} files"
            )
        else:
            lines.append(
                f"\u2713 Key #{key_index}: {_mask_key(key)} "
                f"\u2192 {file_count} files (Loaded: {loaded_total})"
            )

    lines.append("")
    lines.append("ERROR AUDIT")
    lines.append("\u2501" * 40)

    error_entries = []
    for r in results:
        if r.status == "SKIPPED":
            error_entries.append(
                f"\u2022 File {r.filename}: LOADED NUMBER NOT CAPTURED (3s timeout)"
            )
        elif r.status == "ERROR":
            error_entries.append(
                f"\u2022 File {r.filename}: API DRAINED at {r.bot_count or 0} numbers"
            )

    if error_entries:
        lines.extend(error_entries)
    else:
        lines.append("[None]")

    lines.append("")
    lines.append(f"FINAL STATUS: {final_status}")
    lines.append("\u2501" * 40)
    lines.append("[WORKFLOW ENDED - PRESS ENTER TO EXIT]")

    return "\n".join(lines)
