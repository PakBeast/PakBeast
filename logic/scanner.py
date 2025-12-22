"""File scanning logic for finding parameters, properties, and blocks."""

import re
from pathlib import Path
from typing import List, Optional

from core.constants import PARAM_RE, PROP_RE, DELETABLE_BLOCK_HEADER_RE
from core.models import ModEdit


def _find_block_context_name(target_line: int, lines: List[str]) -> Optional[str]:
    """
    Finds the name of the block containing target_line. Used for single lookups from the UI.
    Scans upwards, tracking brace depth, to find the block header.
    It prioritizes the first quoted string in the header's parameters as the name.
    If none is found, it uses the first unquoted parameter.
    If that fails, it uses the block type itself (e.g., "Item").
    """
    brace_depth = 0
    # Scan upwards from the line *before* the target.
    for i in range(target_line - 1, -1, -1):
        line = lines[i]
        brace_depth += line.count('}')
        brace_depth -= line.count('{')

        # When brace_depth becomes negative, we have found the '{' that opens the containing block.
        if brace_depth < 0:
            # The header is likely on this line or a few lines above.
            # Combine a few lines to handle multi-line declarations.
            search_area = " ".join(lines[max(0, i - 4) : i + 1])
            
            # Look for the pattern: BlockType(...)
            # Use finditer to get the last match, as it's closest to the block opening.
            last_match = None
            for m in re.finditer(r'(\w+)\s*\(([^)]*)\)', search_area.replace('\n', ' ')):
                last_match = m
            match = last_match

            if match:
                block_type = match.group(1)
                params_str = match.group(2)

                # Priority 1: Find the first quoted string.
                quoted_match = re.search(r'"([^"]+)"', params_str)
                if quoted_match:
                    return quoted_match.group(1).strip()

                # Priority 2: Find the first unquoted parameter if it's a valid identifier.
                unquoted_match = re.match(r'\s*([a-zA-Z0-9_]+)', params_str)
                if unquoted_match:
                    return unquoted_match.group(1).strip()

                # Priority 3: Fallback to the block type.
                return block_type
            
            # Fallback for simple headers like 'sub SubName {'
            simple_match = re.search(r'sub\s+([a-zA-Z0-9_]+)', search_area.replace('\n', ' '))
            if simple_match:
                return simple_match.group(1).strip()

            # Found the block but no recognizable header, stop searching upwards for this context.
            return None
            
    return None  # Scanned to top of file without finding context


def find_block_bounds(lines: List[str], start_ln: int) -> int:
    """Finds the end line of a block starting at start_ln by counting braces."""
    brace_depth = 0
    has_opened = False
    for i in range(start_ln, len(lines)):
        line_content = lines[i]
        if '{' in line_content:
            has_opened = True
            brace_depth += line_content.count('{')
        brace_depth -= line_content.count('}')
        if has_opened and brace_depth <= 0:
            return i
    return -1


def scan_scr_for_hits(file_path: Path, kws: List[str]) -> List[ModEdit]:
    """
    Optimized single-pass scanner. Finds Param/Property/Block matches in one .scr file.
    It iterates through the file once, tracking block context with a stack, which is much
    faster than re-scanning for the context of every match.
    """
    hits: List[ModEdit] = []
    if not kws:
        return hits
    try:
        lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return hits
    
    context_stack: List[str] = []
    level_stack: List[int] = []  # Tracks the brace level for each context on the stack
    brace_level = 0
    potential_header_buffer: List[str] = []

    for ln, line in enumerate(lines):
        stripped = line.strip()
        
        # 1. Pop contexts that are closed by a '}' on this line.
        # A context at level N is closed when the brace_level drops below N.
        if '}' in line:
            brace_level -= line.count('}')
            while level_stack and brace_level < level_stack[-1]:
                level_stack.pop()
                context_stack.pop()
        
        # 2. Check for property hits on the current line using the current context.
        current_context = context_stack[-1] if context_stack else None
        
        if m_block := DELETABLE_BLOCK_HEADER_RE.search(line):
            block_type, block_name = m_block.groups()
            search_context = f"{block_type.lower()} {block_name.lower().replace('_', ' ')}"
            if all(kw in search_context for kw in kws):
                end_ln = find_block_bounds(lines, ln)
                if end_ln != -1:
                    hits.append(ModEdit(
                        str(file_path), ln, f'Block("{block_name}")', "<DELETED>",
                        f'{block_type}: "{block_name}"', block_type,
                        edit_type='BLOCK_DELETE', end_line_number=end_ln
                    ))

        if m_param := PARAM_RE.search(line):
            pname, val = m_param.groups()
            # Include context, param name, AND value for case-insensitive search
            search_context = (current_context or "").lower().replace('_', ' ') + " " + pname.lower() + " " + val.lower()
            if all(kw in search_context for kw in kws):
                hits.append(ModEdit(
                    str(file_path), ln, val, val, current_context or pname, pname, is_param=True
                ))

        if pm := PROP_RE.search(line):
            pname, oval = pm.groups()
            # Include context, property name, AND value for case-insensitive search
            search_context = (current_context or "").lower().replace('_', ' ') + " " + pname.lower() + " " + oval.strip().lower()
            if all(kw in search_context for kw in kws):
                hits.append(ModEdit(
                    str(file_path), ln, oval.strip(), oval.strip(),
                    current_context or Path(file_path).stem, pname, is_param=False
                ))

        # 3. Buffer potential header lines.
        if stripped and not stripped.startswith(('//', '#')):
            potential_header_buffer.append(stripped)

        # 4. If an opening brace is found, process the buffer to find and push the new context.
        if '{' in line:
            header_text = " ".join(potential_header_buffer)
            name = None
            last_match = None
            for m in re.finditer(r'(\w+)\s*\(([^)]*)\)', header_text):
                last_match = m
            
            if last_match:
                block_type, params_str = last_match.groups()
                quoted_match = re.search(r'"([^"]+)"', params_str)
                if quoted_match:
                    name = quoted_match.group(1).strip()
                else:
                    unquoted_match = re.match(r'\s*([a-zA-Z0-9_]+)', params_str)
                    if unquoted_match:
                        name = unquoted_match.group(1).strip()
                    else:
                        name = block_type
            else:
                simple_match = re.search(r'sub\s+([a-zA-Z0-9_]+)', header_text)
                if simple_match:
                    name = simple_match.group(1).strip()
            
            if name:
                # Push context and its brace level *before* adding the current line's '{'
                context_stack.append(name)
                level_stack.append(brace_level)

            potential_header_buffer = []  # Clear buffer after processing
            brace_level += line.count('{')
        
        # If a line contains a property, it's not a header line, so clear buffer.
        elif stripped and (PROP_RE.search(stripped) or PARAM_RE.search(stripped)):
            potential_header_buffer = []
            
    return hits