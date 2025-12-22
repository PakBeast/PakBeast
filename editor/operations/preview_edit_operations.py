"""Preview-specific edit operations (right-click menu, line insertion, etc.)."""

import re
from pathlib import Path
from tkinter import messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App

from core.constants import PARAM_RE, PROP_RE, DELETABLE_BLOCK_HEADER_RE
from core.models import ModEdit
from logic.scanner import find_block_bounds, _find_block_context_name
from dialogs.input_dialog import InputDialog


def on_preview_right_click(app: 'App', event):
    """Handle right-click on preview panel."""
    if not app.current_file:
        return
    
    import tkinter as tk
    
    index = app.txt.index(f"@{event.x},{event.y}")
    ln = int(index.split(".")[0]) - 1
    line = app.txt.get(f"{ln + 1}.0", f"{ln + 1}.end")

    menu = tk.Menu(app, tearoff=0)
    is_block_header = re.search(r'^\s*(Action|AttackPreset|Item|Set|PerceptionPreset)\s*\(', line)
    
    menu.add_command(label="Insert Line Above", command=lambda: add_line_insertion_edit(app, ln, below=False))
    menu.add_command(label="Insert Line Below", command=lambda: add_line_insertion_edit(app, ln, below=True))
    menu.add_separator()

    if line.strip() and not is_block_header:
        menu.add_command(label="Modify Line", command=lambda: add_line_edit(app, ln))

    if PROP_RE.search(line) or PARAM_RE.search(line):
        menu.add_command(label="Delete Line", command=lambda: add_line_deletion_edit(app, ln))

    if is_block_header:
        if menu.index('end') is not None:
            menu.add_separator()
        menu.add_command(label="Delete Block", command=lambda: trigger_block_deletion(app, ln))

    if menu.index('end') is not None:
        menu.post(event.x_root, event.y_root)


def add_line_insertion_edit(app: 'App', ln: int, below: bool):
    """Add a line insertion edit."""
    if not app.current_file:
        return
    
    dialog = InputDialog(
        app,
        "Insert Line",
        f"Enter text for the new line to insert {'below' if below else 'above'} line {ln+1}:",
        ""
    )
    new_line = dialog.result

    if new_line is not None:
        target_ln = ln + 1 if below else ln
        
        existing_inserts = [
            e.insertion_index for e in app.active_edits.values() 
            if e.file_path == str(app.current_file) and e.line_number == target_ln and e.edit_type == 'LINE_INSERT'
        ]
        insertion_index = max(existing_inserts) + 1 if existing_inserts else 1

        edit = ModEdit(
            file_path=str(app.current_file),
            line_number=target_ln,
            original_value="<INSERT>",
            current_value=new_line,
            description=f"Insert at line {target_ln+1}",
            param_name="<Line Insert>",
            edit_type='LINE_INSERT',
            insertion_index=insertion_index,
        )
        app.active_edits[edit.key()] = edit
        app.project_is_dirty = True
        from .edits import refresh_edits_list
        refresh_edits_list(app)


def add_line_edit(app: 'App', ln: int):
    """Add a line replacement edit."""
    if not app.current_file:
        return
        
    original_line = app.txt.get(f"{ln + 1}.0", f"{ln + 1}.end")
    
    dialog = InputDialog(
        app,
        "Modify Line",
        f"Modify line {ln+1} in {app.current_file.name}:",
        original_line.rstrip('\r\n')
    )
    new_line = dialog.result

    if new_line is not None and new_line != original_line.rstrip('\r\n'):
        edit = ModEdit(
            file_path=str(app.current_file),
            line_number=ln,
            original_value=original_line,
            current_value=new_line,
            description=f"Line {ln+1}",
            param_name="<Line Edit>",
            edit_type='LINE_REPLACE'
        )
        app.active_edits[edit.key()] = edit
        app.project_is_dirty = True
        from .edits import refresh_edits_list
        refresh_edits_list(app)


def add_line_deletion_edit(app: 'App', ln: int):
    """Add a line deletion edit."""
    if not app.current_file:
        return
        
    line = app.txt.get(f"{ln + 1}.0", f"{ln + 1}.end")
    pname, oval = "", ""
    if m := PROP_RE.search(line):
        pname, oval = m.groups()
    elif m := PARAM_RE.search(line):
        pname, oval = m.groups()
    else:
        return

    from .preview_handler import find_context_name
    context = find_context_name(app, ln)
    edit = ModEdit(
        file_path=str(app.current_file),
        line_number=ln,
        original_value=oval.strip(),
        current_value=line.strip(),
        description=context or Path(app.current_file).stem,
        param_name=pname,
        edit_type='LINE_DELETE'
    )
    app.active_edits[edit.key()] = edit
    app.project_is_dirty = True
    from .edits import refresh_edits_list
    refresh_edits_list(app)


def trigger_block_deletion(app: 'App', ln: int):
    """Trigger block deletion."""
    if not app.current_file:
        return
    line = app.txt.get(f"{ln+1}.0", f"{ln+1}.end")
    
    m_block = re.search(r'^\s*(Action|AttackPreset|Item|Set|PerceptionPreset)\s*\(\s*"([^"]+)"[^)]*\)', line)
    if not m_block:
        return

    app.txt.config(state="normal")
    lines = app.txt.get("1.0", "end-1c").splitlines()
    app.txt.config(state="disabled")

    if (end_ln := find_block_bounds(lines, ln)) != -1:
        block_type, block_name = m_block.groups()
        description = f'{block_type}: "{block_name}"'
        if messagebox.askyesno(
            "Confirm Block Deletion",
            f"Mark this block for deletion?\n\n"
            f"Block: {description}\n\n"
            f"Warning: This action cannot be undone."
        ):
            edit = ModEdit(
                str(app.current_file), ln, f'Block("{block_name}")', "<DELETED>",
                description, block_type, edit_type='BLOCK_DELETE', end_line_number=end_ln
            )
            app.active_edits[edit.key()] = edit
            app.project_is_dirty = True
            from .edits import refresh_edits_list
            refresh_edits_list(app)

