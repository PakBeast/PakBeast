"""Text viewer UI component for displaying full text differences."""

import customtkinter as ctk
from pathlib import Path
from typing import Optional

from ..operations.models import FileDiff
from ..operations.text_comparison import compare_plain_text_files


def populate_text_viewer(
    text_viewer: ctk.CTkTextbox,
    diff: FileDiff,
    original_path: Optional[Path],
    modded_path: Optional[Path],
    context: int,
) -> None:
    """Populate the text viewer with full text differences."""
    # For TXT file comparisons, comparison text should already be populated
    # But if it's not, try to refresh using stored file paths
    if diff.diff is None:
        # Check if file paths are stored as attributes
        orig_file = getattr(diff, 'original_file', None)
        mod_file = getattr(diff, 'modded_file', None)
        
        if orig_file and mod_file and orig_file.exists() and mod_file.exists():
            refreshed_comparisons = compare_plain_text_files(
                original_path=orig_file,
                modded_path=mod_file,
                context=context,
                include_diff=True,
                max_text_bytes=1_000_000,
            )
            if refreshed_comparisons:
                refreshed = refreshed_comparisons[0]
                diff.diff = refreshed.diff
                diff.param_changes = refreshed.param_changes
                diff.diff_truncated = refreshed.diff_truncated
                diff.changed_lines = refreshed.changed_lines

    # Populate comparison text
    text_viewer.configure(state="normal")
    text_viewer.delete("1.0", "end")
    if diff.diff_truncated:
        text_viewer.insert("1.0", "[Comparison text skipped: file too large for in-app view]\n")
    # Convert tabs to spaces for consistent display (matching Notepad++ behavior)
    diff_content = (diff.diff or "[No comparison text]")
    if diff_content != "[No comparison text]":
        diff_content = diff_content.expandtabs(tabsize=4)
    text_viewer.insert("1.0", diff_content)
    text_viewer.configure(state="disabled")
