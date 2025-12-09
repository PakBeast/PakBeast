"""Packing operations for creating .pak files."""

import os
import shutil
import tempfile
import threading
import zipfile
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from core.app import App
    from core.models import ModEdit

from core.constants import APP_NAME, PARAM_RE, PROP_RE


class PackingWarning:
    """Simple class to represent warnings during packing (not errors)."""
    def __init__(self, message: str):
        self.message = message
    def __str__(self):
        return self.message


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
            if not pak_path.exists():
                print(f"WARNING: Multi-pack file not found: {pak_path_str}")
                continue
            try:
                with zipfile.ZipFile(pak_path, 'r') as zf:
                    for member in zf.infolist():
                        # Skip directories (zipfile directories end with '/')
                        if member.filename.endswith('/'):
                            continue
                        target_path = staging_dir / member.filename
                        if target_path.exists() and not app.settings.multi_pack_overwrite:
                            continue # Keep existing file, do not overwrite
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(target_path, 'wb') as f:
                            f.write(zf.read(member))
            except Exception as e:
                print(f"ERROR: Failed to process multi-pack file {pak_path_str}: {e}")
                # Continue with other pak files even if one fails

        # 2. Apply this mod's edits
        edits_by_file: Dict[str, List[ModEdit]] = {}
        failed_edits: List[str] = []
        for ed in app.active_edits.values():
            if ed.is_enabled:
                edits_by_file.setdefault(ed.file_path, []).append(ed)

        for fpath, edits in edits_by_file.items():
            p = Path(fpath)
            if app.temp_root and p.is_relative_to(app.temp_root):
                # Get relative path and normalize to forward slashes (zipfile format)
                rel_path = p.relative_to(app.temp_root)
                rel_path_str = str(rel_path).replace(os.sep, "/")
            else:
                rel_path_str = p.name
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
                    applied = False
                    if (m := PARAM_RE.search(orig)) and e.param_name == m.group(1):
                        # Robustly replace the value, preserving original whitespace
                        value_span = m.span(2)
                        modified_lines[e.line_number] = orig[:value_span[0]] + e.current_value + orig[value_span[1]:]
                        applied = True
                    elif (pm := PROP_RE.search(orig)) and pm.group(1) == e.param_name:
                        # Robustly replace the value for properties, preserving original whitespace
                        value_span = pm.span(2)
                        modified_lines[e.line_number] = orig[:value_span[0]] + e.current_value + orig[value_span[1]:]
                        applied = True
                    
                    if not applied:
                        # Log warning if edit couldn't be applied - this helps users debug issues
                        file_name = Path(fpath).name
                        warning_msg = f"Could not apply edit for '{e.param_name}' on line {e.line_number + 1} of {file_name}"
                        print(f"WARNING: {warning_msg}")
                        print(f"  Line content: {orig.strip()}")
                        print(f"  Expected param name: {e.param_name}")
                        print(f"  Expected value: {e.current_value}")
                        failed_edits.append(f"{file_name}:{e.line_number + 1} ({e.param_name})")
                        
                        # Try to still apply if we can find the param name even if regex doesn't match perfectly
                        # This handles edge cases where the line format might be slightly different
                        if e.param_name in orig:
                            # Fallback: try a simple string replacement if param name exists
                            # Find the param and replace its value more carefully
                            param_pattern = f'Param("{e.param_name}",'
                            if param_pattern in orig:
                                # Try to find and replace just the value part
                                import re as re_module
                                fallback_pattern = re_module.compile(
                                    rf'Param\("{re_module.escape(e.param_name)}",\s*("[^"]+"|\S+)'
                                )
                                if fallback_match := fallback_pattern.search(orig):
                                    fallback_span = fallback_match.span(2)
                                    modified_lines[e.line_number] = orig[:fallback_span[0]] + e.current_value + orig[fallback_span[1]:]
                                    applied = True
                                    print(f"  ✓ Applied using fallback method")

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
        # Pass failed edits info to the completion handler
        warning = None
        if failed_edits:
            warning = PackingWarning(f"Some edits could not be applied:\n" + "\n".join(f"  - {fe}" for fe in failed_edits))
        app.after(0, _packing_finished, app, out_path, warning)
    except Exception as e:
        if 'staging_dir' in locals() and staging_dir.exists():
            shutil.rmtree(staging_dir)
        app.after(0, _packing_finished, app, out_path, e)


def _packing_finished(app: 'App', out_path, error: Optional[Exception]):
    """Handle packing completion."""
    app._hide_progress()
    if error:
        if isinstance(error, PackingWarning):
            # It's a warning about failed edits - show warning but don't fail completely
            if hasattr(app, '_update_status'):
                app._update_status(f"Packed with warnings: {Path(out_path).name}", "#FF9800")  # Orange
            else:
                app.status.set(f"Packed with warnings: {Path(out_path).name}")
            messagebox.showwarning(
                APP_NAME,
                f"Mod package compiled with warnings.\n\n"
                f"{error}\n\n"
                f"Please check the console output for details. The mod may not have all intended changes applied."
            )
        else:
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

