"""Edit filtering and sorting operations."""

import threading
import time
from pathlib import Path
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App
    from core.models import ModEdit


def get_filtered_and_sorted_edits(app: 'App') -> List['ModEdit']:
    """Returns a filtered and sorted list of edits based on the current filter settings.
    
    This function is thread-safe and can be called from background threads.
    It reads filter values from the app state at the time of call.
    """
    current_type_filter = app.filter_edit_type.get()
    current_file_filter = app.filter_file_path.get()
    search_query = app.search_edits_var.get().lower().strip()
    
    # Create a snapshot of active_edits to avoid issues if it changes during filtering
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


def filter_edits_in_background(app: 'App') -> None:
    """Filter edits in a background thread for large datasets.
    
    This function should be called from the main thread. It will:
    1. Check if background filtering is needed (>= 1000 items)
    2. If needed, start a background thread to perform filtering
    3. Update UI asynchronously when filtering completes
    """
    total_edits = len(app.active_edits)
    
    # Capture filter values on main thread BEFORE starting background thread
    # Tkinter variables are not thread-safe to read from background threads
    current_type_filter = app.filter_edit_type.get()
    current_file_filter = app.filter_file_path.get()
    search_query = app.search_edits_var.get().lower().strip()
    
    # Always use background threading if there's a search query (string matching can be slow)
    # For small datasets without search, filter synchronously for instant feedback
    if total_edits < 500 and not search_query:
        # Use the existing refresh function for small datasets without search (synchronous, instant)
        from operations.edits.list_management import refresh_edits_list
        refresh_edits_list(app)
        return
    
    # Create snapshot of active_edits on main thread
    edits_snapshot = list(app.active_edits.values())
    
    # For large datasets, use background threading
    if hasattr(app, '_is_filtering') and app._is_filtering:
        # If filtering is already in progress, cancel and restart
        if hasattr(app, '_filter_thread') and app._filter_thread.is_alive():
            # Note: We can't actually cancel a running thread, but we can ignore its result
            # by checking a flag. For now, we'll just let it complete.
            pass
    
    app._is_filtering = True
    
    # Show filtering status
    app.after(0, lambda: _show_filtering_status(app, total_edits))
    
    # Start background filtering thread with captured values
    filter_thread = threading.Thread(
        target=_run_filtering_in_background,
        args=(app, edits_snapshot, current_type_filter, current_file_filter, search_query),
        daemon=True
    )
    app._filter_thread = filter_thread
    filter_thread.start()


def _run_filtering_in_background(
    app: 'App',
    edits_snapshot: List['ModEdit'],
    current_type_filter: str,
    current_file_filter: str,
    search_query: str
) -> None:
    """Run filtering in background thread.
    
    All Tkinter variable values and data snapshots are passed as parameters
    to avoid thread-safety issues.
    """
    try:
        # Use the snapshot passed from main thread (no Tkinter variable access)
        edits = edits_snapshot
        total_edits = len(edits)
        
        # Apply filters
        if current_type_filter != "All Edit Types":
            edits = [e for e in edits if e.edit_type == current_type_filter]
        
        if current_file_filter != "All Files":
            edits = [e for e in edits if Path(e.file_path).name == current_file_filter]

        if search_query:
            # Process in chunks with yields to prevent stuttering
            # This allows the UI to remain responsive during filtering
            filtered_edits = []
            chunk_size = 200  # Smaller chunks for better responsiveness
            total_items = len(edits)
            processed = 0
            
            for i in range(0, total_items, chunk_size):
                end_idx = min(i + chunk_size, total_items)
                chunk_results = []
                
                # Process this chunk
                for j in range(i, end_idx):
                    e = edits[j]
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
                        chunk_results.append(e)
                
                filtered_edits.extend(chunk_results)
                processed = end_idx
                
                # Update progress periodically
                if total_items >= 1000 and processed % 1000 == 0:
                    def update_progress(p=processed, t=total_items):
                        if hasattr(app, '_update_status'):
                            app._update_status(f"Filtering... ({p}/{t} items)", "#2196F3")
                        elif hasattr(app, 'status'):
                            app.status.set(f"Filtering... ({p}/{t} items)")
                    app.after(0, update_progress)
                
                # Yield control to other threads (allows UI to update)
                # Small sleep allows the main thread to process events
                if end_idx < total_items:
                    time.sleep(0.001)  # 1ms yield to other threads
            
            edits = filtered_edits
        
        # Sort the results (only if we didn't use chunked search processing)
        sort_key = lambda e: (Path(e.file_path).name, e.line_number, e.insertion_index, e.edit_type)
        filtered_edits = sorted(edits, key=sort_key)
        
        # Update UI on main thread
        app.after(0, lambda: _finish_filtering(app, filtered_edits))
        
    except Exception as e:
        # On error, fall back to synchronous filtering
        import traceback
        print(f"Background filtering error: {e}")
        traceback.print_exc()
        try:
            filtered_edits = get_filtered_and_sorted_edits(app)
            app.after(0, lambda: _finish_filtering(app, filtered_edits))
        except Exception:
            app.after(0, lambda: _finish_filtering(app, []))


def _show_filtering_status(app: 'App', total_edits: int) -> None:
    """Show filtering status in UI."""
    if hasattr(app, '_update_status'):
        app._update_status(f"Filtering {total_edits} modifications...", "#2196F3")
    elif hasattr(app, 'status'):
        app.status.set(f"Filtering {total_edits} modifications...")


def _finish_filtering(app: 'App', filtered_edits: List['ModEdit']) -> None:
    """Finish filtering and update UI."""
    app._is_filtering = False
    
    # Update the edits list UI
    _update_edits_list_ui(app, filtered_edits)
    
    # Update status
    result_count = len(filtered_edits)
    if hasattr(app, '_update_status'):
        app._update_status(f"Ready ({result_count} modification(s) shown)", "#4CAF50")
    elif hasattr(app, 'status'):
        app.status.set(f"Ready ({result_count} modification(s) shown)")


def _update_edits_list_ui(app: 'App', filtered_edits: List['ModEdit']) -> None:
    """Update the edits list UI with filtered results.
    
    This function must be called from the main thread (via app.after()).
    """
    # Import here to avoid circular import
    from operations.edits.list_management import refresh_edits_list_with_results
    refresh_edits_list_with_results(app, filtered_edits)
