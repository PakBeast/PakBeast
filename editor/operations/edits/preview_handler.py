"""Preview double-click handling and context finding."""

import re
import tkinter as tk
from tkinter import messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App

from core.constants import APP_NAME, PARAM_RE, PROP_RE, DELETABLE_BLOCK_HEADER_RE
from core.models import ModEdit
from logic.scanner import find_block_bounds
from ..preview_handler import find_context_name
from .list_management import refresh_edits_list


def on_preview_double_click(app: 'App', _evt=None) -> None:
    """Handle double-click on preview."""
    if not app.current_file:
        return
    index = app.txt.index(f"@{app.txt.winfo_pointerx()-app.txt.winfo_rootx()},{app.txt.winfo_pointery()-app.txt.winfo_rooty()}")
    ln = int(index.split(".")[0]) - 1
    line = app.txt.get(f"{ln+1}.0", f"{ln+1}.end")

    if m_block := DELETABLE_BLOCK_HEADER_RE.search(line):
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
                refresh_edits_list(app)
            return

    candidate = None
    if m_param := PARAM_RE.search(line):
        pname, val = m_param.groups()
        context = find_context_name(app, ln)
        candidate = ModEdit(str(app.current_file), ln, val, val, context or pname, pname, is_param=True)
    elif m_prop := PROP_RE.search(line):
        pname, oval = m_prop.groups()
        context = find_context_name(app, ln)
        
        description = context or pname
        if pname == "Action":
            action_name_match = re.search(r'"([^"]+)"', oval)
            if action_name_match:
                description = action_name_match.group(1)

        candidate = ModEdit(str(app.current_file), ln, oval.strip(), oval.strip(), description, pname, is_param=False)

    if not candidate:
        return
    
    # Prepare default value for dialog
    default_val = candidate.current_value
    if default_val.startswith('"') and default_val.endswith('"') and ',' not in default_val:
        default_val = default_val[1:-1]

    # Use the new custom dialog
    from dialogs.edit import EditDialog
    initial_desc = candidate.param_name if candidate.is_param else candidate.description
    dialog = EditDialog(app, "Modify Property", candidate.param_name, initial_desc, default_val)
    if dialog.result is None:
        return  # User cancelled

    new_desc, new_val_str = dialog.result
    
    final_val = new_val_str
    if candidate.original_value.startswith('"') and not (new_val_str.startswith('"') and new_val_str.endswith('"')) and ',' not in new_val_str:
        final_val = f'"{new_val_str}"'
    
    key = candidate.key()
    if key in app.active_edits:
        app.active_edits[key].current_value = final_val
        app.active_edits[key].description = new_desc
    else:
        candidate.current_value = final_val
        candidate.description = new_desc
        app.active_edits[key] = candidate
    app.project_is_dirty = True
    refresh_edits_list(app)
