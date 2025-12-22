"""Parsing utilities for extracting parameter changes and changed lines from diffs."""

import re
from typing import List, Sequence


def _parse_params(lines: Sequence[str]) -> dict[str, str]:
    """
    Parse parameters from lines into a mapping.
    Supports multiple formats matching the project's regex patterns:
    1. Param("Name", "Value"); - quoted string value
    2. Param("Name", value); - unquoted value (number, boolean, etc.)
    3. FunctionName(value); - function call with semicolon
    4. FunctionName(value) { - function call starting a block
    """
    # Pattern 1: Param("Name", value); format
    # Matches: Param("Name", "Value") or Param("Name", 123) or Param("Name", true)
    # Uses the same pattern as core/constants.py PARAM_RE
    param_re = re.compile(r'Param\("([^"]+)",\s*(".*?"|\S+)\)\s*;')
    
    # Pattern 2: FunctionName(value); or FunctionName(value) { format
    # Matches: EnergyDrainPerSecond(0.25); or Name("value") {
    # Uses the same pattern as core/constants.py PROP_RE (excludes Param to avoid double-matching)
    prop_re = re.compile(r'^\s*(?!Param\b)(\w+)\s*\((.*?)\)\s*(?:;|\{)')
    
    result: dict[str, str] = {}
    for line in lines:
        # Try Param format first (matches both quoted and unquoted values)
        m = param_re.search(line)
        if m:
            name = m.group(1)
            value = m.group(2).strip()
            # Remove quotes if present (for string values)
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            result[name] = value
            continue
        
        # Try function-call format (property format)
        m = prop_re.search(line)
        if m:
            name = m.group(1)
            value = m.group(2).strip()
            # Remove quotes if present (for string values)
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            # Store the value (can be number, string, boolean, or empty)
            result[name] = value
    
    return result


def _extract_changed_lines(diff_str: str) -> List[tuple[str | None, str | None, int | None, int | None]]:
    """
    Extract paired changed lines from a unified diff string with line numbers.
    Only pairs consecutive -/+ lines within the same hunk to avoid false matches.
    Returns: List of (old_line, new_line, old_line_num, new_line_num)
    
    Note: Unified diff uses 1-based line numbers. The hunk header format is:
    @@ -old_start,old_count +new_start,new_count @@
    where old_start and new_start are the starting line numbers (1-based).
    """
    lines = diff_str.splitlines()
    changes: List[tuple[str | None, str | None, int | None, int | None]] = []
    old_line_num: int | None = None
    new_line_num: int | None = None
    last_was_minus = False
    last_minus_content: str | None = None
    last_minus_line_num: int | None = None
    
    for line in lines:
        # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
        # old_start and new_start are 1-based line numbers
        if line.startswith("@@"):
            match = re.search(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
            if match:
                # Reset line numbers to the starting line from the hunk header
                # Note: unified diff uses 1-based line numbers
                old_start = int(match.group(1))
                new_start = int(match.group(3))
                # Validate line numbers are reasonable (sanity check to catch parsing errors)
                # Most files won't exceed 10 million lines, but we allow up to 100 million as a safety limit
                if old_start > 0 and new_start > 0 and old_start <= 100000000 and new_start <= 100000000:
                    old_line_num = old_start
                    new_line_num = new_start
                else:
                    # Invalid line numbers (likely a parsing error), skip this hunk
                    old_line_num = None
                    new_line_num = None
            else:
                # If we can't parse the hunk header, reset to None
                old_line_num = None
                new_line_num = None
            # Reset state for new hunk
            last_was_minus = False
            last_minus_content = None
            last_minus_line_num = None
            continue
        # Skip diff file headers
        if line.startswith("---") or line.startswith("+++"):
            continue
        # Skip empty lines in diff
        if not line:
            continue
        
        # Check for - line (removed/changed)
        if line.startswith("-") and not line.startswith("--"):
            content = line[1:]
            if old_line_num is not None:
                # Store the current line number before incrementing
                last_minus_content = content
                last_minus_line_num = old_line_num
                last_was_minus = True
                # Increment for the next line in the old file
                old_line_num += 1
        # Check for + line (added/changed)
        elif line.startswith("+") and not line.startswith("++"):
            content = line[1:]
            if last_was_minus and last_minus_content is not None and last_minus_line_num is not None:
                # Pair with the immediately preceding - line (same change)
                if new_line_num is not None:
                    # Use the current new_line_num before incrementing
                    changes.append((last_minus_content, content, last_minus_line_num, new_line_num))
                    new_line_num += 1
                else:
                    changes.append((last_minus_content, content, last_minus_line_num, None))
                last_was_minus = False
                last_minus_content = None
                last_minus_line_num = None
            else:
                # Unpaired addition (new line added)
                if new_line_num is not None:
                    # Use the current new_line_num before incrementing
                    changes.append((None, content, None, new_line_num))
                    new_line_num += 1
                else:
                    changes.append((None, content, None, None))
        else:
            # Context line (starts with space) - flush any pending minus as removal
            if last_was_minus and last_minus_content is not None and last_minus_line_num is not None:
                changes.append((last_minus_content, None, last_minus_line_num, None))
                last_was_minus = False
                last_minus_content = None
                last_minus_line_num = None
            # Increment both line counters for context lines
            # Context lines exist in both old and new files
            if old_line_num is not None:
                old_line_num += 1
            if new_line_num is not None:
                new_line_num += 1
    
    # Flush any remaining unpaired removal at end
    if last_was_minus and last_minus_content is not None and last_minus_line_num is not None:
        changes.append((last_minus_content, None, last_minus_line_num, None))
    
    return changes


def _extract_json_key_changes(changed_lines: List[tuple[str | None, str | None, int | None, int | None]]) -> List[tuple[str, str, str]]:
    """
    Extract JSON key-value changes from normalized JSON diff.
    Handles JSON format: "key": value
    """
    json_kv_re = re.compile(r'^\s*"([^"]+)":\s*(.+?)\s*,?\s*$')
    param_changes: List[tuple[str, str, str]] = []
    
    for old_line, new_line, old_line_num, new_line_num in changed_lines:
        old_key = None
        old_value = None
        new_key = None
        new_value = None
        
        if old_line:
            m = json_kv_re.search(old_line)
            if m:
                old_key = m.group(1)
                old_value = m.group(2).strip().rstrip(',').strip()
                # Remove quotes if present
                if old_value.startswith('"') and old_value.endswith('"'):
                    old_value = old_value[1:-1]
        
        if new_line:
            m = json_kv_re.search(new_line)
            if m:
                new_key = m.group(1)
                new_value = m.group(2).strip().rstrip(',').strip()
                # Remove quotes if present
                if new_value.startswith('"') and new_value.endswith('"'):
                    new_value = new_value[1:-1]
        
        # If same key, different value
        if old_key and new_key and old_key == new_key and old_value != new_value:
            param_changes.append((old_key, old_value, new_value))
        # New key
        elif new_key and not old_key:
            param_changes.append((new_key, "", new_value))
        # Removed key
        elif old_key and not new_key:
            param_changes.append((old_key, old_value, ""))
    
    return param_changes


def _extract_param_changes_from_diff(changed_lines: List[tuple[str | None, str | None, int | None, int | None]], is_json: bool = False) -> List[tuple[str, str, str]]:
    """
    Extract parameter changes from changed_lines diff data.
    This captures ALL occurrences of parameter changes, not just the last value per parameter name.
    
    Enhanced to handle:
    - Param("Name", value); format
    - FunctionName(value); format
    - FunctionName(value) { format (function blocks)
    - INI key=value format
    - Indented properties inside blocks
    
    Returns: List of (param_name, old_value, new_value) tuples
    """
    # For JSON files, use JSON-specific extraction
    if is_json:
        return _extract_json_key_changes(changed_lines)
    
    # Pattern 1: Param("Name", value);
    param_re = re.compile(r'Param\("([^"]+)",\s*(".*?"|\S+)\)\s*;')
    
    # Pattern 2: FunctionName(value); or FunctionName(value) { (handles both single-line and block-start)
    # Updated to handle indented lines (not just line start)
    prop_re = re.compile(r'^\s*(?!Param\b)(\w+)\s*\((.*?)\)\s*(?:;|\{)')
    
    # Pattern 3: INI key=value format
    ini_kv_re = re.compile(r'^\s*([^=#\[\s]+?)\s*=\s*(.+?)\s*$')
    
    param_changes: List[tuple[str, str, str]] = []
    
    def extract_param_from_line(line: str) -> tuple[str | None, str | None]:
        """Extract parameter name and value from a line."""
        if not line:
            return None, None
        
        # Try Param format first
        m = param_re.search(line)
        if m:
            name = m.group(1)
            value = m.group(2).strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            return name, value
        
        # Try function-call format (handles both ; and { endings)
        m = prop_re.search(line)
        if m:
            name = m.group(1)
            value = m.group(2).strip()
            # For multi-argument functions, extract the last argument (most common pattern)
            # e.g., bone("PELVIS", "Pelvis") -> extract "Pelvis"
            if ',' in value:
                # Split by comma and take the last part
                parts = [p.strip() for p in value.split(',')]
                if parts:
                    value = parts[-1].strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            return name, value
        
        # Try INI key=value format
        m = ini_kv_re.search(line)
        if m:
            name = m.group(1).strip()
            value = m.group(2).strip()
            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            return name, value
        
        return None, None
    
    for old_line, new_line, old_line_num, new_line_num in changed_lines:
        # Extract parameters from both lines
        old_param, old_value = extract_param_from_line(old_line) if old_line else (None, None)
        new_param, new_value = extract_param_from_line(new_line) if new_line else (None, None)
        
        # If we found a parameter change (same param name, different value)
        if old_param and new_param and old_param == new_param and old_value != new_value:
            param_changes.append((old_param, old_value, new_value))
        # Or if it's a new parameter (only in new line)
        elif new_param and not old_param:
            param_changes.append((new_param, "", new_value))
        # Or if it's a removed parameter (only in old line)
        elif old_param and not new_param:
            param_changes.append((old_param, old_value, ""))
    
    return param_changes
