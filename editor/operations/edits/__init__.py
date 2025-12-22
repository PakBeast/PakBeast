"""Edit operations module."""

from .filtering import get_filtered_and_sorted_edits
from .list_management import refresh_edits_list, selected_edit, on_edit_select
from .operations import toggle_selected_edit, delete_selected_edit, clear_edits, enable_all_filtered, disable_all_filtered
from .context_menu import edits_context
from .editing import edit_selected_value, edit_inserted_text, change_edit_to_delete_line, revert_delete_to_edit
from .preview_handler import on_preview_double_click
from ..preview_handler import find_context_name

__all__ = [
    'get_filtered_and_sorted_edits',
    'refresh_edits_list',
    'selected_edit',
    'on_edit_select',
    'toggle_selected_edit',
    'delete_selected_edit',
    'clear_edits',
    'enable_all_filtered',
    'disable_all_filtered',
    'edits_context',
    'edit_selected_value',
    'edit_inserted_text',
    'change_edit_to_delete_line',
    'revert_delete_to_edit',
    'on_preview_double_click',
    'find_context_name',
]
