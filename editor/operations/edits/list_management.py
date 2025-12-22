"""Edit list management operations."""

from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App
    from core.models import ModEdit

from .filtering import get_filtered_and_sorted_edits


def refresh_edits_list(app: 'App') -> None:
    """Refresh the edits list display and update preview highlighting.
    
    This function automatically uses background threading for large datasets
    to prevent UI freezing. For small datasets, it filters synchronously
    for instant feedback.
    """
    total_edits = len(app.active_edits)
    
    # For large datasets, use background filtering to prevent UI freeze
    if total_edits >= 500:
        from .filtering import filter_edits_in_background
        filter_edits_in_background(app)
        return
    
    # For small datasets, filter synchronously for instant feedback
    filtered_edits = get_filtered_and_sorted_edits(app)
    refresh_edits_list_with_results(app, filtered_edits)


def refresh_edits_list_with_results(app: 'App', filtered_edits: List['ModEdit']) -> None:
    """Refresh the edits list display with pre-filtered results.
    
    This function must be called from the main thread.
    It updates the file filter options and displays the provided filtered edits.
    Uses optimized batch insertion for large lists to prevent UI freezing.
    """
    app.lst_edits.delete(0, "end")
    
    # Update file filter options (only if there are edits to avoid unnecessary work)
    if app.active_edits:
        # Use a set comprehension for efficiency, then sort
        all_files = sorted({Path(e.file_path).name for e in app.active_edits.values()})
        app.file_filter_combo['values'] = ["All Files"] + all_files
    else:
        app.file_filter_combo['values'] = ["All Files"]
    
    # For large lists, use batched insertion with bulk insert operations
    total_items = len(filtered_edits)
    if total_items > 500:
        # Use batched bulk insertion for better performance
        _insert_edits_batched_bulk(app, filtered_edits)
    else:
        # For small lists, format all items and insert in one bulk operation
        formatted_items = [_format_edit_string(ed) for ed in filtered_edits]
        if formatted_items:
            app.lst_edits.insert("end", *formatted_items)
            app.lst_edits.update_idletasks()
    
    # Refresh preview highlighting for edited lines
    if hasattr(app, 'current_file') and app.current_file:
        from ..preview_handler import refresh_edited_lines
        refresh_edited_lines(app)


def _format_edit_string(ed: 'ModEdit') -> str:
    """Format a single edit and return the formatted string (does not insert into listbox)."""
    chk = "☑" if ed.is_enabled else "☐"
    
    if ed.edit_type == 'BLOCK_DELETE':
        return f'{chk}  [DELETE BLOCK] {ed.description}'
    elif ed.edit_type == 'LINE_DELETE':
        # Truncate value if too long
        value_display = ed.current_value
        if len(value_display) > 28:
            value_display = value_display[:25] + "..."
        return f'{chk}  [DELETE] {ed.description}: {value_display}'
    elif ed.edit_type == 'LINE_REPLACE':
        # Truncate value if too long
        value_display = ed.current_value
        if len(value_display) > 28:
            value_display = value_display[:25] + "..."
        return f'{chk}  [REPLACE] {ed.description}: "{value_display}"'
    elif ed.edit_type == 'LINE_INSERT':
        # Truncate value if too long
        value_display = ed.current_value
        if len(value_display) > 28:
            value_display = value_display[:25] + "..."
        return f'{chk}  [INSERT] line {ed.line_number+1}: "{value_display}"'
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
            return f"{chk}  {context_part}  •  {ed.param_name}: {original_val} {change_indicator} {current_val}"
        else:
            return f"{chk}  {ed.param_name}: {original_val} {change_indicator} {current_val}"


def _insert_edits_batched_bulk(app: 'App', filtered_edits: List['ModEdit']) -> None:
    """Insert edits in batches using bulk insert operations for optimal performance.
    
    This function formats items in batches and inserts them all at once using
    unpacking, which is much faster than inserting one by one.
    """
    batch_size = 1000  # Larger batches for bulk insertion
    total_items = len(filtered_edits)
    
    def insert_batch(start_idx: int):
        """Insert a single batch of items."""
        end_idx = min(start_idx + batch_size, total_items)
        
        # Format all items in this batch
        batch_items = [_format_edit_string(filtered_edits[i]) for i in range(start_idx, end_idx)]
        
        # Insert all items at once using unpacking (much faster)
        if batch_items:
            app.lst_edits.insert("end", *batch_items)
            app.lst_edits.update_idletasks()  # Force display update
        
        # Schedule next batch if there are more items
        if end_idx < total_items:
            # Use after_idle for better responsiveness
            app.after_idle(lambda: insert_batch(end_idx))
        else:
            # All items inserted, refresh preview highlighting
            if hasattr(app, 'current_file') and app.current_file:
                from ..preview_handler import refresh_edited_lines
                refresh_edited_lines(app)
    
    # Start inserting batches
    insert_batch(0)


def selected_edit(app: 'App') -> Optional['ModEdit']:
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
        from ..preview_handler import show_edit_in_preview
        show_edit_in_preview(app, edit)
