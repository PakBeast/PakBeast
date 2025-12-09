"""Edit operations for managing active edits."""

import re
from pathlib import Path
from tkinter import messagebox
from typing import Optional, TYPE_CHECKING, List

if TYPE_CHECKING:
    from core.app import App
    from core.models import ModEdit

from core.constants import APP_NAME, PARAM_RE, PROP_RE
from logic.scanner import find_block_bounds, _find_block_context_name


def get_filtered_and_sorted_edits(app: 'App') -> List[ModEdit]:
    """Returns a filtered and sorted list of edits based on the current filter settings."""
    current_type_filter = app.filter_edit_type.get()
    current_file_filter = app.filter_file_path.get()
    search_query = app.search_edits_var.get().lower().strip()
    
    edits = list(app.active_edits.values())
    
    if current_type_filter != "All Edit Types":
        edits = [e for e in edits if e.edit_type == current_type_filter]
    
    if current_file_filter != "All Files":
        edits = [e for e in edits if Path(e.file_path).name == current_file_filter]

    if search_query:
        filtered_edits = []
        for e in edits:
            # Create the display string to search against it
            chk = "☑" if e.is_enabled else "☐"
            if e.edit_type == 'BLOCK_DELETE':
                shown = f'{chk} [DELETE BLOCK] {e.description}'
            elif e.edit_type == 'LINE_DELETE':
                shown = f'{chk} [DELETE LINE] {e.description}: {e.current_value}'
            elif e.edit_type == 'LINE_REPLACE':
                shown = f'{chk} [EDIT LINE] {e.description}: "{e.current_value}"'
            elif e.edit_type == 'LINE_INSERT':
                shown = f'{chk} [INSERT LINE] at {e.line_number+1}: "{e.current_value}"'
            else:
                shown = f"{chk}  {e.description}: {e.param_name} = {e.current_value}  (was {e.original_value})"

            if search_query in shown.lower():
                filtered_edits.append(e)
        edits = filtered_edits

    sort_key = lambda e: (Path(e.file_path).name, e.line_number, e.insertion_index, e.edit_type)
    return sorted(edits, key=sort_key)


def refresh_edits_list(app: 'App') -> None:
    """Refresh the edits list display."""
    app.lst_edits.delete(0, "end")
    
    # Update file filter options
    all_files = sorted(list({Path(e.file_path).name for e in app.active_edits.values()}))
    app.file_filter_combo['values'] = ["All Files"] + all_files
    
    # Get filtered edits and display them
    filtered_edits = get_filtered_and_sorted_edits(app)
    for ed in filtered_edits:
        chk = "☑" if ed.is_enabled else "☐"
        
        if ed.edit_type == 'BLOCK_DELETE':
            shown = f'{chk}  [DELETE BLOCK] {ed.description}'
        elif ed.edit_type == 'LINE_DELETE':
            # Truncate value if too long
            value_display = ed.current_value
            if len(value_display) > 28:
                value_display = value_display[:25] + "..."
            shown = f'{chk}  [DELETE] {ed.description}: {value_display}'
        elif ed.edit_type == 'LINE_REPLACE':
            # Truncate value if too long
            value_display = ed.current_value
            if len(value_display) > 28:
                value_display = value_display[:25] + "..."
            shown = f'{chk}  [REPLACE] {ed.description}: "{value_display}"'
        elif ed.edit_type == 'LINE_INSERT':
            # Truncate value if too long
            value_display = ed.current_value
            if len(value_display) > 28:
                value_display = value_display[:25] + "..."
            shown = f'{chk}  [INSERT] line {ed.line_number+1}: "{value_display}"'
        else:
            # For VALUE_REPLACE: compact format showing change
            context_part = ed.description if ed.description != ed.param_name else ""
            
            # Truncate values if too long
            current_val = ed.current_value
            if len(current_val) > 18:
                current_val = current_val[:15] + "..."
            original_val = ed.original_value
            if len(original_val) > 18:
                original_val = original_val[:15] + "..."
            
            # Show only if values differ, otherwise show as "unchanged"
            if current_val == original_val:
                change_indicator = "="
            else:
                change_indicator = "→"
            
            if context_part and context_part != ed.param_name:
                shown = f"{chk}  {context_part}  •  {ed.param_name}: {original_val} {change_indicator} {current_val}"
            else:
                shown = f"{chk}  {ed.param_name}: {original_val} {change_indicator} {current_val}"
        
        app.lst_edits.insert("end", shown)


def selected_edit(app: 'App') -> Optional[ModEdit]:
    """Get the currently selected edit."""
    if not (sel := app.lst_edits.curselection()):
        return None
    ordered = get_filtered_and_sorted_edits(app)
    try:
        return ordered[sel[0]]
    except IndexError:
        return None


def on_edit_select(app: 'App', _evt=None):
    """Handle edit selection."""
    if edit := selected_edit(app):
        from .preview_handler import show_edit_in_preview
        show_edit_in_preview(app, edit)


def toggle_selected_edit(app: 'App'):
    """Toggle enabled state of selected edit."""
    if ed := selected_edit(app):
        ed.is_enabled = not ed.is_enabled
        app.project_is_dirty = True
        refresh_edits_list(app)


def delete_selected_edit(app: 'App'):
    """Delete selected edit."""
    if ed := selected_edit(app):
        del app.active_edits[ed.key()]
        app.project_is_dirty = True
        refresh_edits_list(app)


def clear_edits(app: 'App'):
    """Clear all edits."""
    if app.active_edits and messagebox.askyesno(
        APP_NAME,
        "Clear all modifications?\n\n"
        "This will remove all active modifications from the current project.\n"
        "This action cannot be undone."
    ):
        app.active_edits.clear()
        app.project_is_dirty = True
        refresh_edits_list(app)


def edits_context(app: 'App', event) -> None:
    """Show context menu for edits list."""
    import tkinter as tk
    # Select item under cursor before showing menu
    app.lst_edits.selection_clear(0, "end")
    idx = app.lst_edits.nearest(event.y)
    app.lst_edits.selection_set(idx)
    app.lst_edits.activate(idx)
    edit = selected_edit(app)
    
    menu = tk.Menu(app, tearoff=0)
    
    if edit:
        if edit.edit_type == 'VALUE_REPLACE':
            menu.add_command(label="Edit Value and Description", command=lambda: edit_selected_value(app))
            menu.add_command(label="Delete Line", command=lambda: change_edit_to_delete_line(app))
            menu.add_separator()
        elif edit.edit_type == 'LINE_DELETE':
            menu.add_command(label="Revert to Value Modification", command=lambda: revert_delete_to_edit(app))
            menu.add_separator()
        elif edit.edit_type == 'LINE_INSERT':
            menu.add_command(label="Edit Inserted Text", command=lambda: edit_inserted_text(app))
            menu.add_separator()
        
        menu.add_command(label="Toggle Enabled State", command=lambda: toggle_selected_edit(app))
        menu.add_command(label="Remove Modification", command=lambda: delete_selected_edit(app))
    
    menu.post(event.x_root, event.y_root)


def edit_inserted_text(app: 'App'):
    """Edit inserted text."""
    if not (ed := selected_edit(app)) or ed.edit_type != 'LINE_INSERT':
        return
    from dialogs.input_dialog import InputDialog
    dialog = InputDialog(
        app,
        "Modify Inserted Line",
        "Enter new text for the line:",
        ed.current_value
    )
    new_text = dialog.result
    if new_text is not None and new_text != ed.current_value:
        ed.current_value = new_text
        app.project_is_dirty = True
        refresh_edits_list(app)


def edit_selected_value(app: 'App') -> None:
    """Edit selected value."""
    if not (ed := selected_edit(app)) or ed.edit_type != 'VALUE_REPLACE':
        return
    
    initial_val = ed.current_value
    if initial_val.startswith('"') and initial_val.endswith('"') and ',' not in initial_val:
        initial_val = initial_val[1:-1]
    
    from dialogs.edit import EditDialog
    initial_desc = ed.description if not ed.is_param else ed.param_name
    dialog = EditDialog(app, "Modify Property", ed.param_name, initial_desc, initial_val)
    if dialog.result is None:
        return

    new_desc, new_val_str = dialog.result
    final_val = new_val_str
    if ed.original_value.startswith('"') and not (new_val_str.startswith('"') and new_val_str.endswith('"')) and ',' not in new_val_str:
        final_val = f'"{new_val_str}"'
    
    if ed.current_value != final_val or ed.description != new_desc:
        ed.current_value = final_val
        ed.description = new_desc
        app.project_is_dirty = True
        refresh_edits_list(app)


def change_edit_to_delete_line(app: 'App'):
    """Change edit type to delete line."""
    if ed := selected_edit(app):
        try:
            p = Path(ed.file_path)
            lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
            if ed.line_number < len(lines):
                ed.current_value = lines[ed.line_number].strip()
            else:
                ed.current_value = f"{ed.param_name}({ed.original_value});"
        except Exception:
            ed.current_value = f"{ed.param_name}({ed.original_value});"
        ed.edit_type = 'LINE_DELETE'
        app.project_is_dirty = True
        refresh_edits_list(app)


def revert_delete_to_edit(app: 'App'):
    """Revert delete to value edit."""
    if ed := selected_edit(app):
        ed.edit_type = 'VALUE_REPLACE'
        ed.current_value = ed.original_value
        app.project_is_dirty = True
        refresh_edits_list(app)


def enable_all_filtered(app: 'App'):
    """Enable all filtered edits."""
    filtered_edits = get_filtered_and_sorted_edits(app)
    if not filtered_edits:
        return
    for edit in filtered_edits:
        edit.is_enabled = True
    app.project_is_dirty = True
    refresh_edits_list(app)


def disable_all_filtered(app: 'App'):
    """Disable all filtered edits."""
    filtered_edits = get_filtered_and_sorted_edits(app)
    if not filtered_edits:
        return
    for edit in filtered_edits:
        edit.is_enabled = False
    app.project_is_dirty = True
    refresh_edits_list(app)


def on_preview_double_click(app: 'App', _evt=None) -> None:
    """Handle double-click on preview."""
    if not app.current_file:
        return
    import tkinter as tk
    index = app.txt.index(f"@{app.txt.winfo_pointerx()-app.txt.winfo_rootx()},{app.txt.winfo_pointery()-app.txt.winfo_rooty()}")
    ln = int(index.split(".")[0]) - 1
    line = app.txt.get(f"{ln+1}.0", f"{ln+1}.end")

    from core.constants import DELETABLE_BLOCK_HEADER_RE
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
                from core.models import ModEdit
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
        from core.models import ModEdit
        candidate = ModEdit(str(app.current_file), ln, val, val, context or pname, pname, is_param=True)
    elif m_prop := PROP_RE.search(line):
        pname, oval = m_prop.groups()
        context = find_context_name(app, ln)
        
        description = context or pname
        if pname == "Action":
            action_name_match = re.search(r'"([^"]+)"', oval)
            if action_name_match:
                description = action_name_match.group(1)

        from core.models import ModEdit
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


def find_context_name(app: 'App', target_line: int):
    """Find context name for a line."""
    app.txt.config(state="normal")
    lines = app.txt.get("1.0", "end-1c").splitlines()
    app.txt.config(state="disabled")
    return _find_block_context_name(target_line, lines)

