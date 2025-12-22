"""Packer entry point and completion handling."""

import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from core.app import App

from core.constants import APP_NAME
from .builder import build_pak_file
from .models import PackingWarning


def pack_pak(app: 'App') -> None:
    """Pack the mod into a .pak file."""
    if not app.active_edits:
        messagebox.showwarning(
            APP_NAME,
            "Unable to compile mod package.\n\n"
            "No active modifications have been added.\n"
            "Please add modifications before compiling."
        )
        return
    if not (out := filedialog.asksaveasfilename(defaultextension=".pak", filetypes=[("PAK Files", "*.pak"), ("All files", "*.*")])):
        return
    out_name = Path(out).name
    app._show_progress(f"Packing mod: {out_name}...")
    threading.Thread(target=_run_packing_in_background, args=(app, out)).start()


def _run_packing_in_background(app: 'App', out_path: str):
    """Run packing in background thread."""
    staging_dir, warning, error = build_pak_file(app, out_path)
    app.after(0, _packing_finished, app, out_path, warning, error)


def _packing_finished(app: 'App', out_path: str, warning: Optional[PackingWarning], error: Optional[Exception]):
    """Handle packing completion."""
    app._hide_progress()
    if error:
        # It's a real exception/error
        if hasattr(app, '_update_status'):
            app._update_status(f"Packing failed: {error}", "#F44336")  # Red
        else:
            app.status.set(f"Packing failed: {error}")
        messagebox.showerror(
            APP_NAME,
            f"Mod compilation failed.\n\n"
            f"Error details: {error}\n\n"
            f"Please check the file paths and try again."
        )
    elif warning:
        # It's a warning about failed edits - show warning but don't fail completely
        if hasattr(app, '_update_status'):
            app._update_status(f"Packed with warnings: {Path(out_path).name}", "#FF9800")  # Orange
        else:
            app.status.set(f"Packed with warnings: {Path(out_path).name}")
        messagebox.showwarning(
            APP_NAME,
            f"Mod package compiled with warnings.\n\n"
            f"{warning}\n\n"
            f"Please check the console output for details. The mod may not have all intended changes applied."
        )
        # Clear dirty flag after successful packing since mod has been exported
        app.project_is_dirty = False
    else:
        out_name = Path(out_path).name
        if hasattr(app, '_update_status'):
            app._update_status(f"Packed mod: {out_name}", "#4CAF50")  # Green
        else:
            app.status.set(f"Packed mod: {out_name}")
        # Clear dirty flag after successful packing since mod has been exported
        app.project_is_dirty = False
        messagebox.showinfo(
            APP_NAME,
            f"Mod package compiled successfully.\n\n"
            f"Output file: {out_path}\n\n"
            f"The mod is ready to use."
        )
