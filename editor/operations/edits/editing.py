"""Edit value editing operations."""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App

from .list_management import selected_edit, refresh_edits_list


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
