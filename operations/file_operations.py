"""File operations for loading, saving, and managing pak files."""

import os
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
from core.settings import write_json, read_json


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
    app.preview_label.configure(text="File Preview: —")
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


def populate_tree(app: 'App', root: Path) -> None:
    """Populate the file tree with extracted files."""
    from ui.utils import shorten_path
    
    app.path_to_id.clear()
    # Root shows just the name
    root_id = app.tree.insert("", "end", text=root.name, values=(str(root),), open=True)
    app.path_to_id[root] = root_id
    app.tree.set(root_id, "abspath", str(root))
    app.tree.set(root_id, "tooltip", root.name)
    
    for dirpath, dirnames, filenames in os.walk(root):
        parent_path = Path(dirpath)
        parent_id = app.path_to_id.get(parent_path)
        if parent_id is None:
            continue
        dirnames.sort()
        filenames.sort()
        
        for name in dirnames:
            full_path = parent_path / name
            # Show just the name (tree structure shows hierarchy), but shorten very long names
            display_text = name if len(name) <= 50 else shorten_path(name, max_length=50)
            rel_path = full_path.relative_to(root) if root else Path(name)
            
            item_id = app.tree.insert(
                parent_id, "end", text=display_text, values=(str(full_path),)
            )
            app.path_to_id[full_path] = item_id
            app.tree.set(item_id, "abspath", str(full_path))
            # Store full relative path for tooltip
            app.tree.set(item_id, "tooltip", str(rel_path))
        
        for name in filenames:
            full_path = parent_path / name
            # Show just the name (tree structure shows hierarchy), but shorten very long names
            display_text = name if len(name) <= 50 else shorten_path(name, max_length=50)
            rel_path = full_path.relative_to(root) if root else Path(name)
            
            item_id = app.tree.insert(
                parent_id, "end", text=display_text, values=(str(full_path),)
            )
            app.path_to_id[full_path] = item_id
            app.tree.set(item_id, "abspath", str(full_path))
            # Store full relative path for tooltip
            app.tree.set(item_id, "tooltip", str(rel_path))


def save_project(app: 'App') -> None:
    """Save the current project to a .pbm file."""
    if not app.temp_root:
        messagebox.showwarning(
            APP_NAME,
            "No game data loaded.\n\n"
            "Please load a game data file (.pak) before saving a project."
        )
        return
    p = filedialog.asksaveasfilename(
        initialdir=app.settings.last_project_dir,
        defaultextension=".pbm",
        filetypes=[("PakBeast Project", "*.pbm"), ("All files", "*.*")]
    )
    if not p:
        return
    app.settings.last_project_dir = str(Path(p).parent)
    app.settings.save()
    edit_count = len(app.active_edits)
    app._show_progress(f"Saving project with {edit_count} edit(s)...")
    try:
        payload = {
            "edits": [
                {
                    **ed.__dict__,
                    "file_path": str(Path(ed.file_path).relative_to(app.temp_root))
                }
                for ed in app.active_edits.values()
            ]
        }
        write_json(Path(p), payload)
        app._hide_progress()
        if hasattr(app, '_update_status'):
            app._update_status(f"Project saved: {Path(p).name}", "#4CAF50")  # Green
        else:
            app.status.set(f"Project saved: {Path(p).name}")
            messagebox.showinfo(
                APP_NAME,
                "Project saved successfully.\n\n"
                "Your modifications have been saved and can be loaded later."
            )
        # Set to False at the very end after all UI updates to ensure nothing resets it
        app.project_is_dirty = False
    except Exception as e:
        app._hide_progress()
        messagebox.showerror(
            APP_NAME,
            f"Failed to save project.\n\n"
            f"Error: {e}\n\n"
            f"Your changes have not been saved."
        )
        # Keep project_is_dirty as True since save failed


def load_project(app: 'App') -> None:
    """Load a project from a .pbm file."""
    if app.project_is_dirty and not messagebox.askyesno(
        "Load Project",
        "You have unsaved changes that will be lost.\n\n"
        "Do you want to continue loading the project?"
    ):
        return
    p = filedialog.askopenfilename(
        initialdir=app.settings.last_project_dir,
        filetypes=[("PakBeast Project", "*.pbm"), ("All files", "*.*")]
    )
    if not p:
        return
    app.settings.last_project_dir = str(Path(p).parent)
    app.settings.save()
    app._show_progress(f"Loading project: {Path(p).name}...")
    data = read_json(Path(p), None)
    if not data or "edits" not in data:
        app._hide_progress()
        messagebox.showerror(
            APP_NAME,
            "Invalid project file.\n\n"
            "The selected file does not appear to be a valid PakBeast project file.\n"
            "Please select a file with the .pbm extension."
        )
        return
    if not app.temp_root:
        app._hide_progress()
        messagebox.showwarning(
            APP_NAME,
            "Game data required.\n\n"
            "Please load the corresponding game data file (.pak) first,\n"
            "then load the project file."
        )
        return
    app.active_edits.clear()
    from core.models import ModEdit
    edit_count = len(data.get("edits", []))
    for i, d in enumerate(data["edits"]):
        d.setdefault('is_param', False)
        d.setdefault('insertion_index', 0)
        me = ModEdit(
            file_path=str(app.temp_root / d["file_path"]),
            **{k: v for k, v in d.items() if k != "file_path"}
        )
        app.active_edits[me.key()] = me
        if (i + 1) % 50 == 0:
            app._show_progress(f"Loading project: {Path(p).name}... ({i+1}/{edit_count} edits)")
    app.project_is_dirty = False
    app._refresh_edits_list()
    app._hide_progress()
    if hasattr(app, '_update_status'):
        app._update_status(f"Project loaded: {Path(p).name} ({edit_count} edits)", "#4CAF50")  # Green
    else:
        app.status.set(f"Project loaded: {Path(p).name} ({edit_count} edits)")
        messagebox.showinfo(
            APP_NAME,
            "Project loaded successfully.\n\n"
            "All modifications have been restored from the project file."
        )

