"""Data models for comparison operations."""

from dataclasses import dataclass
from typing import List


@dataclass
class FileDiff:
    """Represents a difference between two files."""
    path: str
    kind: str  # "added", "removed", "modified-binary", "modified-text"
    diff: str | None = None
    param_changes: List[tuple[str, str, str]] | None = None  # (name, old, new)
    diff_truncated: bool = False
    changed_lines: List[tuple[str | None, str | None, int | None, int | None]] | None = None  # (old_line, new_line, old_line_num, new_line_num)
