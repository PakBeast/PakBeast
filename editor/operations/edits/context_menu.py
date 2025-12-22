"""Context menu operations for edits list."""

import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App

from .list_management import selected_edit
from .operations import toggle_selected_edit, delete_selected_edit
from .editing import edit_selected_value, edit_inserted_text, change_edit_to_delete_line, revert_delete_to_edit


def edits_context(app: 'App', event) -> None:
    """Show context menu for edits list."""
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
