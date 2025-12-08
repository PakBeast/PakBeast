"""Packing operations for creating .pak files."""

import os
import shutil
import tempfile
import threading
import zipfile
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from core.app import App
    from core.models import ModEdit

from core.constants import APP_NAME, PARAM_RE, PROP_RE


def pack_pak(app: 'App') -> None:
    """Pack the mod into a .pak file."""
    if not app.active_edits and not app.settings.multi_pack_files:
        messagebox.showwarning(
            APP_NAME,
            "Unable to compile mod package.\n\n"
            "No active modifications or additional .pak files have been configured.\n"
            "Please add modifications or configure additional .pak files in Settings before compiling."
        )
        return
    if not (out := filedialog.asksaveasfilename(defaultextension=".pak", filetypes=[("PAK Files", "*.pak"), ("All files", "*.*")])):
        return
    out_name = Path(out).name
    app._show_progress(f"Packing mod: {out_name}...")
    threading.Thread(target=_run_packing_in_background, args=(app, out)).start()


def _run_packing_in_background(app: 'App', out_path: str):
    """Run packing in background thread."""
    try:
        out_name = Path(out_path).name
        staging_dir = Path(tempfile.mkdtemp(prefix="pakbeast_pack_"))
        
        # 1. Process multi-pack files
        for pak_path_str in app.settings.multi_pack_files:
            pak_path = Path(pak_path_str)
            if pak_path.exists():
                with zipfile.ZipFile(pak_path, 'r') as zf:
                    for member in zf.infolist():
                        if member.is_dir(): continue
                        target_path = staging_dir / member.filename
                        if target_path.exists() and not app.settings.multi_pack_overwrite:
                            continue # Keep existing file, do not overwrite
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(target_path, 'wb') as f:
                            f.write(zf.read(member))

        # 2. Apply this mod's edits
        edits_by_file: Dict[str, List[ModEdit]] = {}
        for ed in app.active_edits.values():
            if ed.is_enabled:
                edits_by_file.setdefault(ed.file_path, []).append(ed)

        for fpath, edits in edits_by_file.items():
            p = Path(fpath)
            rel_path_str = str(p.relative_to(app.temp_root)) if app.temp_root and p.is_relative_to(app.temp_root) else p.name
            staging_file_path = staging_dir / rel_path_str
            
            if staging_file_path.exists():
                modified_lines = staging_file_path.read_text(encoding="utf-8", errors="ignore").splitlines(True)
            else:
                modified_lines = p.read_text(encoding="utf-8", errors="ignore").splitlines(True)

            edits.sort(key=lambda e: (e.line_number, e.insertion_index), reverse=True)
            for e in edits:
                if e.line_number > len(modified_lines):
                    continue
                if e.edit_type == 'BLOCK_DELETE':
                    del modified_lines[e.line_number : e.end_line_number + 1]
                elif e.edit_type == 'LINE_DELETE':
                    del modified_lines[e.line_number]
                elif e.edit_type == 'LINE_INSERT':
                    ending = '\n'
                    if e.line_number < len(modified_lines) and modified_lines[e.line_number].endswith('\r\n'):
                        ending = '\r\n'
                    elif modified_lines and modified_lines[-1].endswith('\r\n'):
                        ending = '\r\n'
                    modified_lines.insert(e.line_number, e.current_value + ending)
                elif e.edit_type == 'LINE_REPLACE':
                    ending = '\n' if not modified_lines[e.line_number].endswith('\r\n') else '\r\n'
                    modified_lines[e.line_number] = e.current_value + ending
                elif e.edit_type == 'VALUE_REPLACE':
                    orig = modified_lines[e.line_number]
                    if (m := PARAM_RE.search(orig)) and e.param_name == m.group(1):
                        # Robustly replace the value, preserving original whitespace
                        value_span = m.span(2)
                        modified_lines[e.line_number] = orig[:value_span[0]] + e.current_value + orig[value_span[1]:]
                    elif (pm := PROP_RE.search(orig)) and pm.group(1) == e.param_name:
                        # Robustly replace the value for properties, preserving original whitespace
                        value_span = pm.span(2)
                        modified_lines[e.line_number] = orig[:value_span[0]] + e.current_value + orig[value_span[1]:]

            final_content = "".join(modified_lines)
            staging_file_path.parent.mkdir(parents=True, exist_ok=True)
            staging_file_path.write_text(final_content, encoding="utf-8")
        
        # 3. Zip the staging directory
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(staging_dir):
                for file in files:
                    file_path = Path(root) / file
                    archive_path = file_path.relative_to(staging_dir)
                    zf.write(file_path, str(archive_path).replace(os.sep, "/"))

        shutil.rmtree(staging_dir)
        app.after(0, _packing_finished, app, out_path, None)
    except Exception as e:
        if 'staging_dir' in locals() and staging_dir.exists():
            shutil.rmtree(staging_dir)
        app.after(0, _packing_finished, app, out_path, e)


def _packing_finished(app: 'App', out_path, error):
    """Handle packing completion."""
    app._hide_progress()
    if error:
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
    else:
        out_name = Path(out_path).name
        if hasattr(app, '_update_status'):
            app._update_status(f"Packed mod: {out_name}", "#4CAF50")  # Green
        else:
            app.status.set(f"Packed mod: {out_name}")
        messagebox.showinfo(
            APP_NAME,
            f"Mod package compiled successfully.\n\n"
            f"Output file: {out_path}\n\n"
            f"The mod is ready to use."
        )

