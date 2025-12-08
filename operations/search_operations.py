"""Search operations for finding parameters and properties."""

import threading
import concurrent.futures
from functools import partial
from pathlib import Path
from tkinter import messagebox
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from core.app import App
    from core.models import ModEdit

from core.constants import APP_NAME
from logic.scanner import scan_scr_for_hits


def find_params(app: 'App') -> None:
    """Search for parameters matching the search query."""
    if not app.temp_root:
        messagebox.showwarning(
            APP_NAME,
            "No game data loaded.\n\n"
            "Please load a game data file (.pak) before searching."
        )
        return
    if not (query := app.ent_search.get().strip().lower()):
        messagebox.showinfo(
            APP_NAME,
            "Search criteria required.\n\n"
            "Please enter one or more search terms to find parameters or properties."
        )
        return
    kws = query.split()
    app.lst_results.delete(0, "end")
    app.search_results.clear()
    if not (scr_files := [p for p in app.path_to_id if p.name.endswith(".scr")]):
        if hasattr(app, '_update_status'):
            app._update_status("No .scr files found.", "#FF9800")  # Orange
        else:
            app.status.set("No .scr files found.")
        return
    file_count = len(scr_files)
    app._show_progress(f"Searching in {file_count} file(s)...")
    threading.Thread(target=_run_search_in_background, args=(app, scr_files, kws)).start()


def _run_search_in_background(app: 'App', scr_files: List[Path], kws: List[str]):
    """Run search in background thread."""
    scan_func = partial(scan_scr_for_hits, kws=kws)
    results = []
    total_files = len(scr_files)
    processed = 0
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(scan_func, f): f for f in scr_files}
            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())
                processed += 1
                if processed % 10 == 0 or processed == total_files:
                    app.after(0, lambda p=processed, t=total_files: app._show_progress(f"Searching... ({p}/{t} files)"))
    except Exception:
        for i, f in enumerate(scr_files):
            results.extend(scan_func(f))
            if (i + 1) % 10 == 0:
                app.after(0, lambda p=i+1, t=total_files: app._show_progress(f"Searching... ({p}/{t} files)"))
    finally:
        app.after(0, _finish_search, app, results)


def _finish_search(app: 'App', results: List[ModEdit]):
    """Finish search and update UI."""
    from ui.utils import shorten_path
    
    app._hide_progress()
    app.search_results = sorted(
        list({ed.key(): ed for ed in results}.values()),
        key=lambda e: (e.edit_type, Path(e.file_path).name.lower(), e.line_number)
    )
    
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
        
        app.lst_results.insert("end", label)
    
    result_count = len(app.search_results)
    if result_count == 0:
        if hasattr(app, '_update_status'):
            app._update_status("No matches found.", "#FF9800")  # Orange
        else:
            app.status.set("No matches found.")
    else:
        if hasattr(app, '_update_status'):
            app._update_status(f"Found {result_count} match(es)", "#4CAF50")  # Green
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

