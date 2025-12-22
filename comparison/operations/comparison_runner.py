"""Comparison execution logic for TXT file comparison."""

import threading
from pathlib import Path
from typing import Callable, TYPE_CHECKING

from .text_comparison import compare_plain_text_files
from .models import FileDiff

if TYPE_CHECKING:
    from core.app import App


def parse_file_path(file_string: str) -> Path | None:
    """Parse single file path."""
    if not file_string or not file_string.strip():
        return None
    path = Path(file_string.strip())
    return path if path.exists() else None


def run_comparison(
    app: "App",
    original_path: Path,
    modded_path: Path,
    context: int,
    on_complete: Callable[[list[FileDiff], dict], None],
    on_error: Callable[[str], None],
) -> None:
    """
    Run comparison between two TXT files in a background thread.
    
    Args:
        app: Application instance for thread-safe UI updates
        original_path: Path to original TXT file
        modded_path: Path to modded TXT file
        context: Number of context lines for comparison
        on_complete: Callback with (file_comparisons, summary_dict)
        on_error: Callback with error message
    """
    def worker():
        try:
            file_comparisons = compare_plain_text_files(
                original_path=original_path,
                modded_path=modded_path,
                context=context,
                include_diff=True,
                max_text_bytes=1_000_000,
            )
            
            # Store file paths as attributes for later use
            for comparison in file_comparisons:
                comparison.original_file = original_path
                comparison.modded_file = modded_path

            summary = {
                "added": len([d for d in file_comparisons if d.kind == "added"]),
                "removed": len([d for d in file_comparisons if d.kind == "removed"]),
                "modified_text": len([d for d in file_comparisons if d.kind == "modified-text"]),
                "modified_binary": len([d for d in file_comparisons if d.kind == "modified-binary"]),
            }
            
            app.after(0, lambda: on_complete(file_comparisons, summary))

        except Exception as exc:
            app.after(0, lambda: on_error(str(exc)))

    threading.Thread(target=worker, daemon=True).start()
