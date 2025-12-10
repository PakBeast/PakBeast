"""
Run diffs between two pak/zip archives and return structured results.
"""

from __future__ import annotations

import difflib
import re
import zipfile
from pathlib import Path
from typing import List, Sequence, Tuple

from .pak_diff import diff_archives, FileDiff


def _is_text(data: bytes) -> bool:
    if b"\x00" in data:
        return False
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def _decode_text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def _parse_params(lines):
    param_re = re.compile(r'Param\("(?P<name>[^"]+)",\s*"(?P<value>[^"]*)"\);')
    result = {}
    for line in lines:
        m = param_re.search(line)
        if m:
            result[m.group("name")] = m.group("value")
    return result


def run_diff(
    original_path: Path,
    modded_path: Path,
    extensions: Sequence[str],
    context: int,
    include_diff: bool = True,
    max_text_bytes: int = 1_000_000,
) -> Tuple[List[FileDiff], dict]:
    """
    Run archive diff and return both detailed diffs and a summary dict.
    """
    diffs = diff_archives(
        original_path=original_path,
        modded_path=modded_path,
        extensions=[ext.lower() for ext in extensions],
        context=context,
        include_diff=include_diff,
        max_text_bytes=max_text_bytes,
    )
    summary = {
        "added": len([d for d in diffs if d.kind == "added"]),
        "removed": len([d for d in diffs if d.kind == "removed"]),
        "modified_text": len([d for d in diffs if d.kind == "modified-text"]),
        "modified_binary": len([d for d in diffs if d.kind == "modified-binary"]),
    }
    return diffs, summary


def diff_file(
    original_path: Path,
    modded_path: Path,
    rel_path: str,
    context: int,
    max_text_bytes: int = 1_000_000,
) -> FileDiff:
    """Compute diff for a single file path inside two archives."""
    with zipfile.ZipFile(original_path, "r") as zf_orig, zipfile.ZipFile(
        modded_path, "r"
    ) as zf_mod:
        try:
            orig_bytes = zf_orig.read(rel_path)
            mod_bytes = zf_mod.read(rel_path)
        except KeyError:
            # If missing in one archive, treat accordingly
            if rel_path in zf_orig.namelist():
                return FileDiff(path=rel_path, kind="removed")
            if rel_path in zf_mod.namelist():
                return FileDiff(path=rel_path, kind="added")
            return FileDiff(path=rel_path, kind="removed")

    if orig_bytes == mod_bytes:
        return FileDiff(path=rel_path, kind="modified-text", diff="[No changes]", param_changes=None)

    orig_is_text = _is_text(orig_bytes)
    mod_is_text = _is_text(mod_bytes)

    if orig_is_text and mod_is_text:
        orig_text = _decode_text(orig_bytes).splitlines()
        mod_text = _decode_text(mod_bytes).splitlines()
        orig_params = _parse_params(orig_text)
        mod_params = _parse_params(mod_text)
        param_changes: List[tuple[str, str, str]] = []
        for name, old_val in orig_params.items():
            if name in mod_params and mod_params[name] != old_val:
                param_changes.append((name, old_val, mod_params[name]))
        diff_str = None
        diff_truncated = False
        if len(orig_bytes) <= max_text_bytes and len(mod_bytes) <= max_text_bytes:
            diff_lines = difflib.unified_diff(
                orig_text,
                mod_text,
                fromfile=f"original/{rel_path}",
                tofile=f"modded/{rel_path}",
                n=context,
            )
            diff_str = "\n".join(diff_lines)
            from .pak_diff import _extract_changed_lines  # local import to avoid cycle at top
            changed_lines = _extract_changed_lines(diff_str)
        else:
            diff_truncated = True
            changed_lines = None
        return FileDiff(
            path=rel_path,
            kind="modified-text",
            diff=diff_str,
            param_changes=param_changes or None,
            diff_truncated=diff_truncated,
            changed_lines=changed_lines,
        )

    return FileDiff(path=rel_path, kind="modified-binary", diff=None, param_changes=None)

