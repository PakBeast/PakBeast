"""Edit application operations for applying modifications to files."""

import re
from pathlib import Path
from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from core.models import ModEdit

from core.constants import PARAM_RE, PROP_RE


def apply_edits_to_lines(
    modified_lines: List[str],
    edits: List['ModEdit'],
    detected_line_ending: str,
) -> Tuple[List[str], List[str]]:
    """
    Apply edits to file lines.
    
    Args:
        modified_lines: List of file lines (0-indexed)
        edits: List of ModEdit objects to apply (line_number is 0-indexed)
        detected_line_ending: Line ending to use ('\n' or '\r\n')
    
    Returns:
        Tuple of (modified_lines, failed_edits)
        - modified_lines: Updated list of lines
        - failed_edits: List of error messages for edits that couldn't be applied
    """
    failed_edits: List[str] = []
    
    # Handle empty file case
    if not modified_lines:
        for e in edits:
            if e.edit_type != 'LINE_INSERT':
                file_name = Path(e.file_path).name
                failed_edits.append(f"{file_name}:{e.line_number + 1} (file is empty)")
        # Allow LINE_INSERT on empty files (insert at line 0)
        for e in edits:
            if e.edit_type == 'LINE_INSERT' and e.line_number == 0:
                modified_lines.append(e.current_value + '\n')
        return modified_lines, failed_edits
    
    # Use detected line ending (already set above, or default to \n)
    # If not detected yet, detect from existing lines
    if not detected_line_ending or detected_line_ending == '\n':
        for line in modified_lines[:10]:  # Check first 10 lines
            if line.endswith('\r\n'):
                detected_line_ending = '\r\n'
                break
            elif line.endswith('\n'):
                detected_line_ending = '\n'
                break
        # Default to \n if not detected
        if not detected_line_ending:
            detected_line_ending = '\n'
    
    edits.sort(key=lambda e: (e.line_number, e.insertion_index), reverse=True)
    for e in edits:
        # Validate line number bounds (0-indexed)
        if e.line_number < 0 or e.line_number >= len(modified_lines):
            file_name = Path(e.file_path).name
            failed_edits.append(f"{file_name}:{e.line_number + 1} (invalid line number)")
            continue
        
        if e.edit_type == 'BLOCK_DELETE':
            # Validate end line number
            if e.end_line_number < 0 or e.end_line_number >= len(modified_lines):
                file_name = Path(e.file_path).name
                failed_edits.append(f"{file_name}:{e.line_number + 1}-{e.end_line_number + 1} (invalid block bounds)")
                continue
            if e.end_line_number < e.line_number:
                file_name = Path(e.file_path).name
                failed_edits.append(f"{file_name}:{e.line_number + 1}-{e.end_line_number + 1} (end < start)")
                continue
            del modified_lines[e.line_number : e.end_line_number + 1]
        elif e.edit_type == 'LINE_DELETE':
            del modified_lines[e.line_number]
        elif e.edit_type == 'LINE_INSERT':
            # Use detected line ending consistently
            # Allow insertion at end of file (line_number == len(modified_lines))
            if e.line_number > len(modified_lines):
                file_name = Path(e.file_path).name
                failed_edits.append(f"{file_name}:{e.line_number + 1} (invalid insertion point)")
                continue
            modified_lines.insert(e.line_number, e.current_value + detected_line_ending)
        elif e.edit_type == 'LINE_REPLACE':
            # Use detected line ending consistently
            modified_lines[e.line_number] = e.current_value + detected_line_ending
        elif e.edit_type == 'VALUE_REPLACE':
            orig = modified_lines[e.line_number]
            applied = False
            if (m := PARAM_RE.search(orig)) and e.param_name == m.group(1):
                # Robustly replace the value, preserving original whitespace
                value_span = m.span(2)
                modified_lines[e.line_number] = orig[:value_span[0]] + e.current_value + orig[value_span[1]:]
                applied = True
            elif (pm := PROP_RE.search(orig)) and pm.group(1) == e.param_name:
                # Robustly replace the value for properties, preserving original whitespace
                value_span = pm.span(2)
                modified_lines[e.line_number] = orig[:value_span[0]] + e.current_value + orig[value_span[1]:]
                applied = True
            
            if not applied:
                # Try fallback methods before giving up
                # Method 1: Try to find param name even if regex doesn't match perfectly
                if e.param_name in orig:
                    # Fallback: try a simple string replacement if param name exists
                    # Find the param and replace its value more carefully
                    param_pattern = f'Param("{e.param_name}",'
                    if param_pattern in orig:
                        # Try to find and replace just the value part
                        fallback_pattern = re.compile(
                            rf'Param("{re.escape(e.param_name)}",\s*("[^"]+"|\S+)'
                        )
                        if fallback_match := fallback_pattern.search(orig):
                            fallback_span = fallback_match.span(2)
                            modified_lines[e.line_number] = orig[:fallback_span[0]] + e.current_value + orig[fallback_span[1]:]
                            applied = True
                
                # Method 2: Try property pattern if param pattern failed
                if not applied and e.param_name in orig:
                    prop_pattern = re.compile(
                        rf'{re.escape(e.param_name)}\s*\(\s*("[^"]+"|\S+)\s*\)'
                    )
                    if prop_match := prop_pattern.search(orig):
                        prop_span = prop_match.span(1)
                        modified_lines[e.line_number] = orig[:prop_span[0]] + e.current_value + orig[prop_span[1]:]
                        applied = True
                
                # If still not applied, log warning
                if not applied:
                    file_name = Path(e.file_path).name
                    warning_msg = f"Could not apply edit for '{e.param_name}' on line {e.line_number + 1} of {file_name}"
                    print(f"WARNING: {warning_msg}")
                    print(f"  Line content: {orig.strip()}")
                    print(f"  Expected param name: {e.param_name}")
                    print(f"  Expected value: {e.current_value}")
                    failed_edits.append(f"{file_name}:{e.line_number + 1} ({e.param_name})")
    
    return modified_lines, failed_edits
