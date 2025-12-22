"""Main packing builder that orchestrates the packing process."""

import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App
    from core.models import ModEdit

from .file_reader import read_file_for_packing
from .edit_applier import apply_edits_to_lines
from .models import PackingWarning


def build_pak_file(app: 'App', out_path: str) -> tuple[Path, PackingWarning | None, Exception | None]:
    """
    Build the .pak file by applying edits.
    Returns: (staging_dir, warning, error)
    """
    out_name = Path(out_path).name
    staging_dir = Path(tempfile.mkdtemp(prefix="pakbeast_pack_"))
    failed_edits: List[str] = []
    
    try:
        # Apply this mod's edits
        edits_by_file: Dict[str, List[ModEdit]] = {}
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
            
            # Read file with line ending detection
            modified_lines, detected_line_ending, original_ends_with_newline, was_json_formatted = read_file_for_packing(
                app, p, staging_file_path
            )
            
            if not modified_lines:
                failed_edits.append(f"{Path(fpath).name}: File not found")
                continue
            
            # Apply edits
            modified_lines, file_failed_edits = apply_edits_to_lines(
                modified_lines, edits, detected_line_ending
            )
            failed_edits.extend(file_failed_edits)

            # Join lines preserving line endings
            final_content = "".join(modified_lines)
            
            # If this was a JSON file that we formatted, minify it back to match original format
            # (games often expect minified JSON, and it's more efficient)
            if was_json_formatted:
                try:
                    # Parse and minify back to original format (no spaces, compact)
                    json_data = json.loads(final_content)
                    final_content = json.dumps(json_data, separators=(',', ':'), ensure_ascii=False)
                    # Minified JSON typically doesn't have newlines, but preserve original ending if it had one
                except (json.JSONDecodeError, ValueError):
                    # If minification fails, keep formatted version
                    pass
            
            # Preserve original file ending (whether it had trailing newline or not)
            # Check current state
            currently_ends_with_newline = final_content.endswith('\n') or final_content.endswith('\r\n')
            
            # Only adjust if it doesn't match original
            if original_ends_with_newline and not currently_ends_with_newline:
                # Original had trailing newline, add it
                final_content += detected_line_ending
            elif not original_ends_with_newline and currently_ends_with_newline:
                # Original didn't have trailing newline, remove it
                final_content = final_content.rstrip('\n\r')
            
            staging_file_path.parent.mkdir(parents=True, exist_ok=True)
            # Use newline='' to prevent Python from normalizing line endings
            staging_file_path.write_text(final_content, encoding="utf-8", newline='')
        
        # 3. Zip the staging directory
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(staging_dir):
                for file in files:
                    file_path = Path(root) / file
                    archive_path = file_path.relative_to(staging_dir)
                    zf.write(file_path, str(archive_path).replace(os.sep, "/"))

        shutil.rmtree(staging_dir)
        
        # Create warning if there were failed edits
        warning = None
        if failed_edits:
            warning = PackingWarning(f"Some edits could not be applied:\n" + "\n".join(f"  - {fe}" for fe in failed_edits))
        
        return staging_dir, warning, None
    except Exception as e:
        if staging_dir.exists():
            shutil.rmtree(staging_dir)
        return staging_dir, None, e
