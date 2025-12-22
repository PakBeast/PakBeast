"""Edit operations (toggle, delete, clear, enable/disable)."""

from tkinter import messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App

from core.constants import APP_NAME
from .filtering import get_filtered_and_sorted_edits
from .list_management import refresh_edits_list, selected_edit


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
        # If no edits remain, project is no longer dirty
        app.project_is_dirty = len(app.active_edits) > 0
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
        # No edits means nothing unsaved
        app.project_is_dirty = False
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
