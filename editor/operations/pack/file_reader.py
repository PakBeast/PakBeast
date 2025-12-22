"""File reading operations with line ending detection and JSON formatting."""

import json
import os
import zipfile
from pathlib import Path
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App


def read_file_for_packing(
    app: 'App',
    file_path: Path,
    staging_file_path: Path,
) -> Tuple[list[str], str, bool, bool]:
    """
    Read a file for packing, handling line endings and JSON formatting.
    Returns: (modified_lines, detected_line_ending, original_ends_with_newline, was_json_formatted)
    """
    p = file_path
    was_json_formatted = False
    detected_line_ending = '\n'
    original_ends_with_newline = True  # Default assumption
    
    # Read from staging directory if it exists,
    # otherwise read from the ORIGINAL .pak file to avoid double-applying edits
    if staging_file_path.exists():
        # Read from staging and detect line endings
        file_content = staging_file_path.read_text(encoding="utf-8", errors="ignore")
        file_bytes = staging_file_path.read_bytes()
        has_crlf = b'\r\n' in file_bytes
        detected_line_ending = '\r\n' if has_crlf else '\n'
        original_ends_with_newline = file_content.endswith('\n') or file_content.endswith('\r\n')
        modified_lines = file_content.splitlines(True)
        # Normalize line endings
        if modified_lines:
            for i in range(len(modified_lines) - 1):
                if not modified_lines[i].endswith(detected_line_ending):
                    modified_lines[i] = modified_lines[i].rstrip('\r\n') + detected_line_ending
        return modified_lines, detected_line_ending, original_ends_with_newline, was_json_formatted
    else:
        # Read from original .pak file to get unmodified content, then apply edits fresh
        # This avoids double-applying edits if the user saved the file
        if app.current_pak_path and app.temp_root and p.is_relative_to(app.temp_root):
            rel_path = p.relative_to(app.temp_root)
            rel_path_str = str(rel_path).replace(os.sep, "/")
            try:
                with zipfile.ZipFile(app.current_pak_path, 'r') as zf:
                    if rel_path_str in zf.namelist():
                        # Read original file from .pak archive
                        original_content_bytes = zf.read(rel_path_str)
                        
                        # Handle empty files
                        if not original_content_bytes:
                            return [], '\n', False, False
                        
                        original_content = original_content_bytes.decode('utf-8', errors='ignore')
                        
                        # Detect line ending type from original content (check bytes, not decoded string)
                        has_crlf = b'\r\n' in original_content_bytes
                        detected_line_ending = '\r\n' if has_crlf else '\n'
                        
                        # Check if file ends with a newline (preserve this)
                        original_ends_with_newline = original_content.endswith('\n') or original_content.endswith('\r\n')
                        
                        # Handle empty content after decoding
                        if not original_content.strip() and not original_content:
                            return [], detected_line_ending, False, False
                        
                        # Check if this is a JSON file (minified) - format it like the preview does
                        # This ensures line numbers match what the user sees in the preview
                        content_stripped = original_content.strip()
                        is_json_like = (p.suffix.lower() == '.json' or 
                                       p.suffix.lower() == '.gui' or
                                       p.suffix.lower() == '' or
                                       content_stripped.startswith('{') or 
                                       content_stripped.startswith('['))
                        
                        if is_json_like:
                            try:
                                # Format JSON to match preview (adds newlines)
                                json_data = json.loads(original_content)
                                formatted_content = json.dumps(json_data, indent=2, ensure_ascii=False)
                                # Split and normalize to detected line ending type
                                modified_lines = formatted_content.splitlines()
                                # Add detected line ending to all but last line
                                for i in range(len(modified_lines) - 1):
                                    modified_lines[i] += detected_line_ending
                                was_json_formatted = True
                            except (json.JSONDecodeError, ValueError):
                                # Not valid JSON, use as-is with splitlines(True) to preserve endings
                                modified_lines = original_content.splitlines(True)
                                # Normalize line endings to detected type
                                if modified_lines:
                                    for i in range(len(modified_lines) - 1):
                                        if not modified_lines[i].endswith(detected_line_ending):
                                            modified_lines[i] = modified_lines[i].rstrip('\r\n') + detected_line_ending
                            return modified_lines, detected_line_ending, original_ends_with_newline, was_json_formatted
                        else:
                            # Use splitlines(True) to preserve line endings
                            modified_lines = original_content.splitlines(True)
                            # Normalize line endings to detected type for consistency
                            if modified_lines:
                                for i in range(len(modified_lines) - 1):
                                    if not modified_lines[i].endswith(detected_line_ending):
                                        modified_lines[i] = modified_lines[i].rstrip('\r\n') + detected_line_ending
                            return modified_lines, detected_line_ending, original_ends_with_newline, was_json_formatted
                    else:
                        # Fallback to temp_root if not in .pak
                        return _read_from_temp_root(p, detected_line_ending, original_ends_with_newline)
            except Exception:
                # Fallback to temp_root if .pak read fails
                return _read_from_temp_root(p, detected_line_ending, original_ends_with_newline)
        else:
            # Fallback to temp_root if no .pak path available
            return _read_from_temp_root(p, detected_line_ending, original_ends_with_newline)


def _read_from_temp_root(p: Path, detected_line_ending: str, original_ends_with_newline: bool) -> Tuple[list[str], str, bool, bool]:
    """Read file from temp_root with line ending detection."""
    if not p.exists():
        return [], detected_line_ending, original_ends_with_newline, False
    
    try:
        # Read from temp_root and detect line endings
        file_content = p.read_text(encoding="utf-8", errors="ignore")
        
        # Handle empty files
        if not file_content:
            return [], detected_line_ending, False, False
        
        file_bytes = p.read_bytes()
        has_crlf = b'\r\n' in file_bytes
        detected_line_ending = '\r\n' if has_crlf else '\n'
        original_ends_with_newline = file_content.endswith('\n') or file_content.endswith('\r\n')
        modified_lines = file_content.splitlines(True)
        
        # Handle files with no newlines (single line without newline)
        if not modified_lines and file_content:
            modified_lines = [file_content]
        
        # Normalize line endings
        if modified_lines:
            for i in range(len(modified_lines) - 1):
                if not modified_lines[i].endswith(detected_line_ending):
                    modified_lines[i] = modified_lines[i].rstrip('\r\n') + detected_line_ending
        
        return modified_lines, detected_line_ending, original_ends_with_newline, False
    except Exception:
        # Return empty on any read error
        return [], detected_line_ending, original_ends_with_newline, False
