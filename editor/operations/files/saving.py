"""Project saving and loading operations."""

from pathlib import Path
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App

from core.constants import APP_NAME
from core.settings import write_json, read_json


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
    project_path = Path(p)
    
    # Validate project file exists and is readable
    if not project_path.exists():
        app._hide_progress()
        messagebox.showerror(
            APP_NAME,
            "Project file not found.\n\n"
            f"The file '{project_path.name}' does not exist."
        )
        return
    
    # Validate file size (prevent loading corrupted/huge files)
    file_size = project_path.stat().st_size
    if file_size > 10 * 1024 * 1024:  # 10MB limit
        app._hide_progress()
        messagebox.showerror(
            APP_NAME,
            "Project file too large.\n\n"
            f"The file '{project_path.name}' is {file_size / 1024 / 1024:.1f} MB.\n"
            "Project files should be smaller than 10 MB."
        )
        return
    
    # Read and validate JSON structure
    data = read_json(project_path, None)
    if not data:
        app._hide_progress()
        messagebox.showerror(
            APP_NAME,
            "Invalid project file.\n\n"
            "The selected file could not be read or is not valid JSON.\n"
            "The file may be corrupted."
        )
        return
    
    if not isinstance(data, dict):
        app._hide_progress()
        messagebox.showerror(
            APP_NAME,
            "Invalid project file format.\n\n"
            "The file does not contain a valid project structure."
        )
        return
    
    if "edits" not in data:
        app._hide_progress()
        messagebox.showerror(
            APP_NAME,
            "Invalid project file.\n\n"
            "The selected file does not appear to be a valid PakBeast project file.\n"
            "Missing 'edits' section."
        )
        return
    
    if not isinstance(data["edits"], list):
        app._hide_progress()
        messagebox.showerror(
            APP_NAME,
            "Invalid project file format.\n\n"
            "The 'edits' section must be a list."
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
    failed_loads = []
    
    for i, d in enumerate(data["edits"]):
        try:
            # Validate edit data structure
            if not isinstance(d, dict):
                failed_loads.append(f"Edit {i+1}: not a dictionary")
                continue
            
            if "file_path" not in d:
                failed_loads.append(f"Edit {i+1}: missing file_path")
                continue
            
            if "line_number" not in d:
                failed_loads.append(f"Edit {i+1}: missing line_number")
                continue
            
            # Validate line_number is non-negative integer
            if not isinstance(d["line_number"], int) or d["line_number"] < 0:
                failed_loads.append(f"Edit {i+1}: invalid line_number ({d.get('line_number')})")
                continue
            
            # Set defaults for optional fields
            d.setdefault('is_param', False)
            d.setdefault('insertion_index', 0)
            d.setdefault('is_enabled', True)
            d.setdefault('edit_type', 'VALUE_REPLACE')
            
            # Construct file path
            edit_file_path = app.temp_root / d["file_path"]
            
            # Validate file exists (warn but don't fail - file might be in different PAK)
            if not edit_file_path.exists():
                # Still create the edit, but it will fail when applied
                pass
            
            me = ModEdit(
                file_path=str(edit_file_path),
                **{k: v for k, v in d.items() if k != "file_path"}
            )
            app.active_edits[me.key()] = me
            
        except Exception as e:
            failed_loads.append(f"Edit {i+1}: {str(e)}")
            continue
        
        if (i + 1) % 50 == 0:
            app._show_progress(f"Loading project: {Path(p).name}... ({i+1}/{edit_count} edits)")
    
    # Report any failed loads
    if failed_loads:
        warning_msg = f"Loaded {edit_count - len(failed_loads)}/{edit_count} edits successfully.\n\n"
        warning_msg += f"{len(failed_loads)} edit(s) failed to load:\n"
        warning_msg += "\n".join(failed_loads[:5])  # Show first 5
        if len(failed_loads) > 5:
            warning_msg += f"\n... and {len(failed_loads) - 5} more"
        messagebox.showwarning(APP_NAME, warning_msg)
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
