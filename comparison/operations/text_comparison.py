"""Plain text file comparison operations."""

import difflib
import json
from pathlib import Path
from typing import List

from .models import FileDiff
from .utils import _is_text, _decode_text
from .parsing import _parse_params, _extract_changed_lines, _extract_param_changes_from_diff


def _normalize_json(content: str) -> str | None:
    """
    Normalize JSON content by parsing and reformatting.
    This helps compare minified vs formatted JSON.
    Returns normalized JSON string, or None if not valid JSON.
    """
    try:
        json_data = json.loads(content)
        # Reformat with consistent indentation and sorted keys
        return json.dumps(json_data, indent=2, sort_keys=True, ensure_ascii=False)
    except (json.JSONDecodeError, ValueError, TypeError):
        return None


def compare_plain_text_files(
    original_path: Path,
    modded_path: Path,
    context: int,
    include_diff: bool = True,
    max_text_bytes: int = 1_000_000,
) -> List[FileDiff]:
    """Compute differences between two plain text files."""
    comparisons: List[FileDiff] = []
    
    # Read both files
    try:
        with open(original_path, "rb") as f:
            orig_bytes = f.read()
    except (IOError, OSError):
        return comparisons  # File doesn't exist or can't be read
    
    try:
        with open(modded_path, "rb") as f:
            mod_bytes = f.read()
    except (IOError, OSError):
        # Modded file doesn't exist - treat as removed
        if _is_text(orig_bytes):
            orig_text = _decode_text(orig_bytes).splitlines()
            comparisons.append(FileDiff(
                path=original_path.name,
                kind="removed",
                diff=None,
            ))
        return comparisons
    
    # If files are identical, return empty list
    if orig_bytes == mod_bytes:
        return comparisons
    
    orig_is_text = _is_text(orig_bytes)
    mod_is_text = _is_text(mod_bytes)
    
    if orig_is_text and mod_is_text:
        orig_content = _decode_text(orig_bytes)
        mod_content = _decode_text(mod_bytes)
        
        # Check if files are JSON and normalize them
        orig_is_json = False
        mod_is_json = False
        if original_path.suffix.lower() in ['.json', '.gui', '.cfg']:
            normalized_orig = _normalize_json(orig_content)
            normalized_mod = _normalize_json(mod_content)
            if normalized_orig and normalized_mod:
                orig_content = normalized_orig
                mod_content = normalized_mod
                orig_is_json = True
                mod_is_json = True
        
        orig_text = orig_content.splitlines()
        mod_text = mod_content.splitlines()
        
        diff_str = None
        diff_truncated = False
        changed_lines = None
        param_changes: List[tuple[str, str, str]] = []
        
        if include_diff:
            if len(orig_bytes) <= max_text_bytes and len(mod_bytes) <= max_text_bytes:
                diff_lines = difflib.unified_diff(
                    orig_text,
                    mod_text,
                    fromfile=f"original/{original_path.name}",
                    tofile=f"modded/{modded_path.name}",
                    n=context,
                )
                diff_str = "\n".join(diff_lines)
                changed_lines = _extract_changed_lines(diff_str)
                
                # Extract parameter changes from the diff (captures ALL occurrences)
                if changed_lines:
                    # Pass is_json flag for JSON-specific extraction
                    param_changes = _extract_param_changes_from_diff(changed_lines, is_json=(orig_is_json and mod_is_json))
            else:
                diff_truncated = True
                # Fallback to dict-based method if diff is too large
                orig_params = _parse_params(orig_text)
                mod_params = _parse_params(mod_text)
                for name, old_val in orig_params.items():
                    if name in mod_params and mod_params[name] != old_val:
                        param_changes.append((name, old_val, mod_params[name]))
        
        comparisons.append(
            FileDiff(
                path=original_path.name,
                kind="modified-text",
                diff=diff_str,
                param_changes=param_changes or None,
                diff_truncated=diff_truncated,
                changed_lines=changed_lines,
            )
        )
    else:
        comparisons.append(FileDiff(path=original_path.name, kind="modified-binary"))
    
    return comparisons
