"""Preview panel operations for displaying and highlighting file content."""

import json
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App
    from core.models import ModEdit

from core.constants import PARAM_RE, PROP_RE, BLOCK_HEADER_RE, STRING_RE, NUMBER_RE, COMMENT_RE
from logic.scanner import _find_block_context_name


def configure_text_tags(app: 'App'):
    """Configure text tags for syntax highlighting using user-defined colors."""
    # Use user-defined colors from settings
    colors = app.settings.colors
    theme = app.settings.theme
    
    # Configure syntax highlighting tags
    app.txt.tag_configure("param", foreground=colors["param"])
    app.txt.tag_configure("prop", foreground=colors["prop"])
    app.txt.tag_configure("block_header", foreground=colors["block_header"], font=("Consolas", 11, "bold"))
    app.txt.tag_configure("string", foreground=colors["string"])
    app.txt.tag_configure("number", foreground=colors["number"])
    app.txt.tag_configure("comment", foreground=colors["comment"])
    
    # Use user-defined theme colors
    bg = theme["background"]
    fg = theme["foreground"]
    edited_bg = theme["edited_line"]
    
    app.txt.tag_configure("edited_line", background=edited_bg)
    app.txt.config(bg=bg, fg=fg, insertbackground=fg)


def apply_syntax_highlighting(app: 'App'):
    """Apply syntax highlighting to the preview text."""
    app.txt.tag_remove("param", "1.0", "end")
    app.txt.tag_remove("prop", "1.0", "end")
    app.txt.tag_remove("block_header", "1.0", "end")
    app.txt.tag_remove("string", "1.0", "end")
    app.txt.tag_remove("number", "1.0", "end")
    app.txt.tag_remove("comment", "1.0", "end")
    content = app.txt.get("1.0", "end-1c")
    for i, line in enumerate(content.splitlines()):
        line_num_str = str(i + 1)
        # Apply highlighting in order: comments first (so they don't interfere), then others
        # Comments
        for m in COMMENT_RE.finditer(line):
            app.txt.tag_add("comment", f"{line_num_str}.{m.start()}", f"{line_num_str}.{m.end()}")
        # Parameters
        for m in PARAM_RE.finditer(line):
            app.txt.tag_add("param", f"{line_num_str}.{m.start()}", f"{line_num_str}.{m.end()}")
        # Properties
        for m in PROP_RE.finditer(line):
            app.txt.tag_add("prop", f"{line_num_str}.{m.start()}", f"{line_num_str}.{m.end()}")
        # Block headers
        for m in BLOCK_HEADER_RE.finditer(line):
            app.txt.tag_add("block_header", f"{line_num_str}.{m.start()}", f"{line_num_str}.{m.end()}")
        # Strings (but not inside already highlighted params/props/block_headers)
        for m in STRING_RE.finditer(line):
            # Check if this string is already part of a param/prop/block_header tag
            start_idx = f"{line_num_str}.{m.start()}"
            end_idx = f"{line_num_str}.{m.end()}"
            existing_tags = app.txt.tag_names(start_idx)
            if "param" not in existing_tags and "prop" not in existing_tags and "block_header" not in existing_tags:
                app.txt.tag_add("string", start_idx, end_idx)
        # Numbers (but not inside already highlighted elements)
        for m in NUMBER_RE.finditer(line):
            start_idx = f"{line_num_str}.{m.start()}"
            end_idx = f"{line_num_str}.{m.end()}"
            existing_tags = app.txt.tag_names(start_idx)
            if "param" not in existing_tags and "prop" not in existing_tags and "block_header" not in existing_tags and "string" not in existing_tags:
                app.txt.tag_add("number", start_idx, end_idx)
    
    # Update line numbers after highlighting
    if hasattr(app, '_update_line_numbers'):
        app._update_line_numbers()


def _is_binary_file(path: Path) -> bool:
    """Check if a file is likely binary."""
    try:
        with open(path, 'rb') as f:
            chunk = f.read(8192)  # Read first 8KB
            if b'\x00' in chunk:  # Null bytes indicate binary
                return True
            # Check for common binary file signatures
            if chunk.startswith((b'\x89PNG', b'\xff\xd8\xff', b'GIF8', b'BM', b'PK\x03\x04')):
                return True
            # Try to decode as text
            chunk.decode('utf-8', errors='strict')
            return False
    except (UnicodeDecodeError, Exception):
        return True


def on_tree_select_path(app: 'App', path: Path):
    """Handle file selection from tree."""
    app.current_file = path
    if app.temp_root:
        relative_path = path.relative_to(app.temp_root)
        from ui.utils import shorten_path
        label = shorten_path(relative_path, max_length=60)
    else:
        label = path.name
    
    # Count edits for this file
    file_edits = [e for e in app.active_edits.values() if Path(e.file_path) == path]
    edit_count = len(file_edits)
    
    # Get file stats
    try:
        file_size = path.stat().st_size
        if file_size < 1024:
            size_str = f"{file_size:,} bytes"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
    except:
        size_str = "Unknown"
    
    # Check if file is binary
    is_binary = _is_binary_file(path)
    
    # Build enhanced label with file info
    file_ext = path.suffix.upper() if path.suffix else "NO EXT"
    if edit_count > 0:
        info_text = f"{label} • {file_ext} • {size_str} • {edit_count} edit{'s' if edit_count != 1 else ''}"
    else:
        info_text = f"{label} • {file_ext} • {size_str}"
    
    app.preview_label.configure(text=f"File Preview: {info_text}")
    
    # Handle binary files
    if is_binary:
        app.txt.config(state="normal")
        app.txt.delete("1.0", "end")
        app.txt.insert("1.0", f"[Binary File - Cannot Preview]\n\n"
                              f"File: {path.name}\n"
                              f"Size: {size_str}\n"
                              f"Type: Binary file (not text-based)\n\n"
                              f"This file cannot be displayed as text. Binary files like images, "
                              f"compressed archives, or compiled data are not editable in PakBeast.")
        app.txt.tag_remove("highlight", "1.0", "end")
        app.txt.tag_remove("hover", "1.0", "end")
        app.txt.tag_remove("edited_line", "1.0", "end")
        app.txt.config(state="disabled")
        if hasattr(app, '_update_line_numbers'):
            app._update_line_numbers()
        return
    
    # Handle text files
    MAX_PREVIEW_SIZE = 5 * 1024 * 1024  # 5MB limit for preview
    try:
        if file_size > MAX_PREVIEW_SIZE:
            # For very large files, only read first portion
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(MAX_PREVIEW_SIZE)
            content += f"\n\n[File truncated - showing first {MAX_PREVIEW_SIZE / (1024*1024):.1f} MB of {file_size / (1024*1024):.1f} MB total]\n"
            # Convert tabs to spaces for consistent display
            content = content.expandtabs(tabsize=4)
            line_count = len(content.splitlines())
        else:
            content = path.read_text(encoding="utf-8", errors="ignore")
            # Try to format JSON files for better readability
            # Check if content looks like JSON (starts with { or [) regardless of file extension
            content_stripped = content.strip()
            if (path.suffix.lower() == '.json' or 
                path.suffix.lower() == '' or 
                content_stripped.startswith('{') or 
                content_stripped.startswith('[')):
                try:
                    # Attempt to parse and pretty-print JSON
                    json_data = json.loads(content)
                    content = json.dumps(json_data, indent=2, ensure_ascii=False)
                except (json.JSONDecodeError, ValueError):
                    # Not valid JSON or parsing failed, use original content
                    pass
            line_count = len(content.splitlines())
    except Exception as e:
        content = f"[Error reading file]\n\nFile: {path.name}\nError: {str(e)}\n\n"
        content += "This file could not be read. It may be corrupted, locked, or in an unsupported format."
        line_count = 0
    
    # Convert tabs to spaces for consistent display (matching Notepad++ behavior)
    # This ensures tabs are displayed as 4 spaces, matching Notepad++ default
    content = content.expandtabs(tabsize=4)
    
    app.txt.config(state="normal")
    app.txt.delete("1.0", "end")
    app.txt.insert("1.0", content)
    app.txt.tag_remove("highlight", "1.0", "end")
    app.txt.tag_remove("hover", "1.0", "end")
    app.txt.tag_remove("edited_line", "1.0", "end")
    
    # Highlight lines with edits
    if file_edits:
        for edit in file_edits:
            if edit.is_enabled:
                start_line = edit.line_number + 1
                end_line = edit.end_line_number + 1
                app.txt.tag_add("edited_line", f"{start_line}.0", f"{end_line}.end")
    
    apply_syntax_highlighting(app)
    app.txt.config(state="disabled")
    
    # Update line numbers
    if hasattr(app, '_update_line_numbers'):
        app._update_line_numbers()
    
    # Update header with line count
    if line_count > 0:
        if edit_count > 0:
            info_text = f"{label} • {file_ext} • {size_str} • {line_count:,} lines • {edit_count} edit{'s' if edit_count != 1 else ''}"
        else:
            info_text = f"{label} • {file_ext} • {size_str} • {line_count:,} lines"
        app.preview_label.configure(text=f"File Preview: {info_text}")


def find_context_name(app: 'App', target_line: int) -> Optional[str]:
    """Find the context name for a given line."""
    app.txt.config(state="normal")
    lines = app.txt.get("1.0", "end-1c").splitlines()
    app.txt.config(state="disabled")
    return _find_block_context_name(target_line, lines)


def refresh_edited_lines(app: 'App'):
    """Refresh the edited line highlighting in the preview."""
    if not app.current_file:
        return
    
    app.txt.config(state="normal")
    app.txt.tag_remove("edited_line", "1.0", "end")
    
    # Highlight lines with edits for the current file
    file_edits = [e for e in app.active_edits.values() if Path(e.file_path) == app.current_file and e.is_enabled]
    for edit in file_edits:
        start_line = edit.line_number + 1
        end_line = edit.end_line_number + 1
        app.txt.tag_add("edited_line", f"{start_line}.0", f"{end_line}.end")
    
    app.txt.config(state="disabled")
    
    # Update header with edit count and file info
    if app.temp_root:
        relative_path = app.current_file.relative_to(app.temp_root)
        from ui.utils import shorten_path
        label = shorten_path(relative_path, max_length=60)
    else:
        label = app.current_file.name
    
    edit_count = len(file_edits)
    file_ext = app.current_file.suffix.upper() if app.current_file.suffix else "NO EXT"
    
    try:
        file_size = app.current_file.stat().st_size
        if file_size < 1024:
            size_str = f"{file_size:,} bytes"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
    except:
        size_str = "Unknown"
    
    # Get line count from current content
    try:
        content = app.txt.get("1.0", "end-1c")
        line_count = len([l for l in content.splitlines() if l.strip() and not l.startswith("[")])
        if line_count > 0:
            if edit_count > 0:
                info_text = f"{label} • {file_ext} • {size_str} • {line_count:,} lines • {edit_count} edit{'s' if edit_count != 1 else ''}"
            else:
                info_text = f"{label} • {file_ext} • {size_str} • {line_count:,} lines"
        else:
            if edit_count > 0:
                info_text = f"{label} • {file_ext} • {size_str} • {edit_count} edit{'s' if edit_count != 1 else ''}"
            else:
                info_text = f"{label} • {file_ext} • {size_str}"
    except:
        if edit_count > 0:
            info_text = f"{label} • {file_ext} • {size_str} • {edit_count} edit{'s' if edit_count != 1 else ''}"
        else:
            info_text = f"{label} • {file_ext} • {size_str}"
    
    app.preview_label.configure(text=f"File Preview: {info_text}")


def show_edit_in_preview(app: 'App', edit: ModEdit):
    """Show and highlight an edit in the preview panel."""
    if not edit:
        return
    file_path = Path(edit.file_path)
    
    def highlight():
        app.txt.config(state="normal")
        app.txt.tag_remove("highlight", "1.0", "end")
        start, end = f"{edit.line_number + 1}.0", f"{edit.end_line_number + 1}.end"
        app.txt.see(start)
        app.txt.tag_add("highlight", start, end)
        refresh_edited_lines(app)  # Refresh edited line indicators
        app.txt.config(state="disabled")

    if app.current_file != file_path:
        item_id = app.path_to_id.get(file_path)
        if item_id and app.tree.exists(item_id):
            app.tree.selection_set(item_id)
            app.tree.focus(item_id)
            app.tree.see(item_id)
            app.after(50, highlight)
        else:
            on_tree_select_path(app, file_path)
            app.after(50, highlight)
    else:
        highlight()

