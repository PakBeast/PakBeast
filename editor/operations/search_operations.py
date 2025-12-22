"""Search operations for finding parameters and properties."""

import os
import time
import threading
import concurrent.futures
from functools import partial
from pathlib import Path
from tkinter import messagebox
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from core.app import App
    from core.models import ModEdit

from core.constants import APP_NAME
from core.file_types import SUPPORTED_SEARCH_EXTENSIONS
from logic.scanner import scan_scr_for_hits


def find_params(app: 'App') -> None:
    """Search for parameters, properties, and blocks matching the search query."""
    if not app.temp_root:
        # Update search status to show the issue (no messagebox - status indicator shows it)
        if hasattr(app, 'search_status'):
            app.search_status.set("No PAK loaded")
        elif hasattr(app, '_update_status'):
            app._update_status("No game data loaded. Please load a PAK file first.", "#FF9800")
        else:
            app.status.set("No game data loaded. Please load a PAK file first.")
        return
    if not (query := app.ent_search.get().strip().lower()):
        # Update search status to show the issue (no messagebox - status indicator shows it)
        if hasattr(app, 'search_status'):
            app.search_status.set("Enter search terms")
        elif hasattr(app, '_update_status'):
            app._update_status("Search criteria required. Please enter search terms.", "#FF9800")
        else:
            app.status.set("Search criteria required. Please enter search terms.")
        return
    kws = query.split()
    app.lst_results.delete(0, "end")
    app.search_results.clear()
    
    # Debug: Check if path_to_id exists and has files
    if not hasattr(app, 'path_to_id') or not app.path_to_id:
        if hasattr(app, 'search_status'):
            app.search_status.set("No files loaded")
        elif hasattr(app, '_update_status'):
            app._update_status("No files loaded. Please load a PAK file first.", "#FF9800")  # Orange
        else:
            app.status.set("No files loaded. Please load a PAK file first.")
        return
    
    searchable_files = [p for p in app.path_to_id
                       if p.suffix.lower() in SUPPORTED_SEARCH_EXTENSIONS]
    
    if not searchable_files:
        total_files = len(app.path_to_id)
        if hasattr(app, 'search_status'):
            app.search_status.set(f"No searchable files ({total_files} total)")
        elif hasattr(app, '_update_status'):
            extensions_found = set(p.suffix.lower() for p in app.path_to_id if p.suffix)
            app._update_status(
                f"No searchable files found. Found {total_files} file(s) with extensions: {', '.join(sorted(extensions_found)) or 'none'}",
                "#FF9800"
            )
        else:
            app.status.set(f"No searchable files found. Found {total_files} file(s).")
        return
    
    file_count = len(searchable_files)
    # Start spinner animation
    _start_search_spinner(app)
    # Start search in background thread
    search_thread = threading.Thread(target=_run_search_in_background, args=(app, searchable_files, kws), daemon=True)
    search_thread.start()


def _start_search_spinner(app: 'App') -> None:
    """Start search status indicator (static, no animation to avoid UI stutter)."""
    if hasattr(app, 'search_status'):
        app.search_status.set("Searching...")
    elif hasattr(app, '_update_status'):
        app._update_status("Searching...", "#2196F3")
    else:
        app.status.set("Searching...")


def _stop_search_spinner(app: 'App') -> None:
    """Stop search status indicator."""
    # Nothing to do - status will be updated in _finish_search
    pass


def _run_search_in_background(app: 'App', searchable_files: List[Path], kws: List[str]):
    """
    Run search in background thread using chunked processing with yield points.
    
    Why chunked processing is necessary:
    - Search is CPU-bound (96% CPU, 3% I/O) - see SEARCH_CPU_VS_IO_EXPLANATION.md
    - Unlike PAK extraction (I/O-bound), search requires regex matching and parsing
    - CPU operations don't yield to OS automatically, causing UI stutter
    - Chunked processing breaks CPU work into manageable batches
    
    Modern approach (2025 best practices):
    - Processes files in smaller chunks (50 files per batch)
    - Yields to UI thread between batches (10ms pause) to prevent stutter
    - Uses smaller thread pools per batch (max 8 workers) to reduce CPU spikes
    - All UI updates scheduled via app.after(0, ...) on main thread
    """
    scan_func = partial(scan_scr_for_hits, kws=kws)
    total_files = len(searchable_files)
    
    # Chunk size: Process files in batches to allow UI to breathe
    # Smaller chunks = more responsive UI, larger chunks = faster processing
    CHUNK_SIZE = 50  # Process 50 files per batch
    
    # Smaller worker count per chunk to reduce CPU spikes
    cpu_count = os.cpu_count() or 4
    max_workers_per_chunk = min(cpu_count, 8, CHUNK_SIZE)  # Max 8 workers per chunk
    
    def scan_file_safe(file_path: Path) -> List:
        """Scan file with error handling, returns empty list on error."""
        try:
            return scan_func(file_path)
        except Exception as file_error:
            print(f"Error scanning {file_path}: {file_error}")
            return []  # Return empty list on error
    
    all_results = []
    processed = 0
    
    try:
        # Process files in chunks
        for chunk_start in range(0, total_files, CHUNK_SIZE):
            chunk_end = min(chunk_start + CHUNK_SIZE, total_files)
            chunk_files = searchable_files[chunk_start:chunk_end]
            
            # Process this chunk in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers_per_chunk) as executor:
                result_iter = executor.map(scan_file_safe, chunk_files)
                
                # Collect results from this chunk
                chunk_results = []
                for file_results in result_iter:
                    chunk_results.extend(file_results)
                
                all_results.extend(chunk_results)
                processed += len(chunk_files)
            
            # Yield to UI thread after each chunk (let UI breathe)
            # This prevents CPU spikes from accumulating
            if chunk_end < total_files:  # Not the last chunk
                # Small delay to let UI process events
                time.sleep(0.01)  # 10ms pause between chunks
    
    except Exception as e:
        # Fallback to sequential processing if thread pool fails
        import traceback
        print(f"Search error: {e}")
        traceback.print_exc()
        all_results = []
        for f in searchable_files:
            try:
                all_results.extend(scan_func(f))
            except Exception as file_error:
                print(f"Error scanning {f}: {file_error}")
    
    finally:
        # Schedule UI update on main thread (non-blocking)
        app.after(0, _finish_search, app, all_results)


def _finish_search(app: 'App', results: List[ModEdit]):
    """Finish search and update UI - all work done on main thread to avoid stutter."""
    from ui.utils import shorten_path
    
    # Clear searching flag
    app._is_searching = False
    
    app._hide_progress()
    
    # Process and sort results (this is fast, done on main thread)
    app.search_results = sorted(
        list({ed.key(): ed for ed in results}.values()),
        key=lambda e: (e.edit_type, Path(e.file_path).name.lower(), e.line_number)
    )
    
    # Populate results list efficiently
    app.lst_results.delete(0, "end")
    result_items = []
    for ed in app.search_results:
        if ed.edit_type == 'BLOCK_DELETE':
            # For blocks: compact format without file path
            label = f"[BLOCK] {ed.description}"
        else:
            # For params/properties: compact format with clear structure
            context_part = ed.description if ed.description != ed.param_name else ""
            
            # Format value for display (truncate if too long)
            value_display = ed.current_value
            if len(value_display) > 20:
                value_display = value_display[:17] + "..."
            
            # Format: context • param = value (without file path)
            if context_part and context_part != ed.param_name:
                # Only show context if it's different from param name
                label = f"{context_part}  •  {ed.param_name} = {value_display}"
            else:
                label = f"{ed.param_name} = {value_display}"
        
        result_items.append(label)
    
    # Insert all items at once (more efficient than one-by-one)
    if result_items:
        app.lst_results.insert(0, *result_items)
    
    result_count = len(app.search_results)
    # Update search status with result count
    if hasattr(app, 'search_status'):
        if result_count == 0:
            app.search_status.set("No matches found")
        else:
            app.search_status.set(f"Found {result_count} match(es)")
    elif hasattr(app, '_update_status'):
        if result_count == 0:
            app._update_status("No matches found.", "#FF9800")  # Orange
        else:
            app._update_status(f"Found {result_count} match(es)", "#4CAF50")  # Green
    else:
        if result_count == 0:
            app.status.set("No matches found.")
        else:
            app.status.set(f"Found {result_count} match(es)")


def on_result_select(app: 'App', _evt=None) -> None:
    """Handle result selection."""
    if sel := app.lst_results.curselection():
        from .preview_handler import show_edit_in_preview
        show_edit_in_preview(app, app.search_results[sel[0]])


def on_add_from_result(app: 'App', _evt=None) -> None:
    """Add selected result to active edits."""
    if not (sel := app.lst_results.curselection()):
        return
    ed = app.search_results[sel[0]]
    if ed.edit_type == 'BLOCK_DELETE':
        from tkinter import messagebox
        if messagebox.askyesno(
            "Confirm Block Deletion",
            f"Mark this block for deletion?\n\n"
            f"Block: {ed.description}\n\n"
            f"This action cannot be undone."
        ):
            app.active_edits[ed.key()] = ed
            app.project_is_dirty = True
            app._refresh_edits_list()
        return

    default_val = ed.current_value
    if default_val.startswith('"') and default_val.endswith('"') and ',' not in default_val:
        default_val = default_val[1:-1]
    
    from dialogs.edit import EditDialog
    initial_desc = ed.param_name if ed.is_param else ed.description
    dialog = EditDialog(app, "Add Modification", ed.param_name, initial_desc, default_val)
    if dialog.result is None:
        return
    
    new_desc, new_val_str = dialog.result
    final_val = new_val_str
    if ed.original_value.startswith('"') and not (new_val_str.startswith('"') and new_val_str.endswith('"')) and ',' not in new_val_str:
        final_val = f'"{new_val_str}"'
    
    ed.current_value = final_val
    ed.description = new_desc
    app.active_edits[ed.key()] = ed
    app.project_is_dirty = True
    app._refresh_edits_list()