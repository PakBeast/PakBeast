"""File loading operations."""

import shutil
import tempfile
import threading
import zipfile
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App

from core.constants import APP_NAME


def load_pak(app: 'App') -> None:
    """Load a .pak file and extract its contents."""
    p = filedialog.askopenfilename(
        initialdir=app.settings.last_pak_dir,
        title="Open Game Data File",
        filetypes=[("PAK/ZIP", "*.pak *.zip"), ("All files", "*.*")]
    )
    if not p:
        return
    app.settings.last_pak_dir = str(Path(p).parent)
    app.settings.save()
    cleanup_temp(app)
    app.current_pak_path = Path(p)
    pak_name = Path(p).name
    app._show_progress(f"Loading {pak_name}...")
    threading.Thread(target=_extract_and_populate, args=(app, p)).start()


def _extract_and_populate(app: 'App', pak_path: str):
    """Extract pak file in background thread."""
    try:
        pak_name = Path(pak_path).name
        app.after(0, lambda: app._show_progress(f"Extracting {pak_name}..."))
        app.temp_root = Path(tempfile.mkdtemp(prefix="pakbeast_data_"))
        with zipfile.ZipFile(pak_path, "r") as zf:
            total_files = len([f for f in zf.namelist() if not f.endswith('/')])
            extracted = 0
            for member in zf.namelist():
                if not member.endswith('/'):
                    zf.extract(member, app.temp_root)
                    extracted += 1
                    if extracted % 100 == 0:
                        app.after(0, lambda e=extracted, t=total_files: app._show_progress(f"Extracting {pak_name}... ({e}/{t} files)"))
        app.after(0, lambda: app._show_progress(f"Building file tree for {pak_name}..."))
        app.after(0, finish_loading, app, pak_name)
    except Exception as e:
        app.after(0, loading_failed, app, e)


def finish_loading(app: 'App', pak_name: str):
    """Finish loading process and update UI."""
    from ..file_tree import populate_tree
    populate_tree(app, app.temp_root)
    file_count = len([p for p in app.path_to_id if p.is_file()])
    app._hide_progress()
    if hasattr(app, '_update_status'):
        app._update_status(f"Loaded {pak_name} ({file_count} files)", "#4CAF50")  # Green
    else:
        app.status.set(f"Loaded {pak_name} ({file_count} files)")


def loading_failed(app: 'App', error: Exception):
    """Handle loading failure."""
    app._hide_progress()
    cleanup_temp(app)
    messagebox.showerror(
        APP_NAME,
        f"Unable to open game data file.\n\n"
        f"Error: {error}\n\n"
        f"Please ensure the file is a valid .pak archive and try again."
    )


def cleanup_temp(app: 'App') -> None:
    """Clean up temporary files and reset UI."""
    app.tree.delete(*app.tree.get_children())
    app.txt.config(state="normal")
    app.txt.delete("1.0", "end")
    app.txt.config(state="disabled")
    app.preview_label.configure(text="File Preview:")
    # Clear line numbers
    if hasattr(app, 'line_numbers'):
        app.line_numbers.config(state="normal")
        app.line_numbers.delete("1.0", "end")
        app.line_numbers.config(state="disabled")
    # Update line numbers to reflect empty state
    if hasattr(app, '_update_line_numbers'):
        app._update_line_numbers()
    app.search_results.clear()
    app.lst_results.delete(0, "end")
    app.active_edits.clear()
    app.project_is_dirty = False
    app.lst_edits.delete(0, "end")
    app.path_to_id.clear()
    if app.temp_root and app.temp_root.exists():
        shutil.rmtree(app.temp_root, ignore_errors=True)
    app.temp_root = None
    app.current_file = None
    app.current_pak_path = None
