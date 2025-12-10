"""
Compare two Dying Light PAK/ZIP archives and print only the differences.

Usage:
    python pak_diff.py --original data0.pak --modded data7.pak \
        [--extensions .scr .cfg .json] [--context 3]

The script:
- Opens both archives without permanently extracting them.
- Compares file presence (added/removed) and content differences.
- For text files, emits unified diffs with a configurable number of context lines.
- Skips identical files and binary blobs by default.
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence


def _read_zip_file(zf: zipfile.ZipFile, name: str) -> bytes:
    """Read a file from the zip, raising a clear error if it fails."""
    with zf.open(name, "r") as fh:
        return fh.read()


def _is_text(data: bytes) -> bool:
    """Heuristic to decide if bytes are text (UTF-8-ish) rather than binary."""
    if b"\x00" in data:
        return False
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def _decode_text(data: bytes) -> str:
    """Decode bytes to text, tolerating errors."""
    return data.decode("utf-8", errors="replace")


@dataclass
class FileDiff:
    path: str
    kind: str  # "added", "removed", "modified-binary", "modified-text"
    diff: str | None = None
    param_changes: List[tuple[str, str, str]] | None = None  # (name, old, new)
    diff_truncated: bool = False
    changed_lines: List[tuple[str | None, str | None, int | None, int | None]] | None = None  # (old_line, new_line, old_line_num, new_line_num)


def _filtered_members(zf: zipfile.ZipFile, extensions: Sequence[str]) -> List[str]:
    """List file members (not directories), optionally filtered by extension."""
    members = []
    for name in zf.namelist():
        if name.endswith("/"):
            continue
        if extensions:
            suffix = Path(name).suffix.lower()
            if suffix not in extensions:
                continue
        members.append(name)
    return members


def _parse_params(lines: Sequence[str]) -> dict[str, str]:
    """Parse Param(\"Name\", \"Value\"); lines into a mapping."""
    param_re = re.compile(r'Param\("(?P<name>[^"]+)",\s*"(?P<value>[^"]*)"\);')
    result: dict[str, str] = {}
    for line in lines:
        m = param_re.search(line)
        if not m:
            continue
        result[m.group("name")] = m.group("value")
    return result


def _extract_changed_lines(diff_str: str) -> List[tuple[str | None, str | None, int | None, int | None]]:
    """
    Extract paired changed lines from a unified diff string with line numbers.
    Only pairs consecutive -/+ lines within the same hunk to avoid false matches.
    Returns: List of (old_line, new_line, old_line_num, new_line_num)
    """
    import re
    lines = diff_str.splitlines()
    changes: List[tuple[str | None, str | None, int | None, int | None]] = []
    old_line_num: int | None = None
    new_line_num: int | None = None
    last_was_minus = False
    last_minus_content: str | None = None
    last_minus_line_num: int | None = None
    
    for line in lines:
        # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
        if line.startswith("@@"):
            match = re.search(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
            if match:
                old_line_num = int(match.group(1))
                new_line_num = int(match.group(3))
            # Reset state for new hunk
            last_was_minus = False
            last_minus_content = None
            last_minus_line_num = None
            continue
        # Skip diff file headers
        if line.startswith("---") or line.startswith("+++"):
            continue
        # Skip empty lines in diff
        if not line:
            continue
        
        # Check for - line (removed/changed)
        if line.startswith("-") and not line.startswith("--"):
            content = line[1:]
            if old_line_num is not None:
                last_minus_content = content
                last_minus_line_num = old_line_num
                last_was_minus = True
                old_line_num += 1
        # Check for + line (added/changed)
        elif line.startswith("+") and not line.startswith("++"):
            content = line[1:]
            if last_was_minus and last_minus_content is not None and last_minus_line_num is not None:
                # Pair with the immediately preceding - line (same change)
                if new_line_num is not None:
                    changes.append((last_minus_content, content, last_minus_line_num, new_line_num))
                    new_line_num += 1
                else:
                    changes.append((last_minus_content, content, last_minus_line_num, None))
                last_was_minus = False
                last_minus_content = None
                last_minus_line_num = None
            else:
                # Unpaired addition (new line added)
                if new_line_num is not None:
                    changes.append((None, content, None, new_line_num))
                    new_line_num += 1
                else:
                    changes.append((None, content, None, None))
        else:
            # Context line (starts with space) - flush any pending minus as removal
            if last_was_minus and last_minus_content is not None and last_minus_line_num is not None:
                changes.append((last_minus_content, None, last_minus_line_num, None))
                last_was_minus = False
                last_minus_content = None
                last_minus_line_num = None
            # Increment both line counters for context
            if old_line_num is not None:
                old_line_num += 1
            if new_line_num is not None:
                new_line_num += 1
    
    # Flush any remaining unpaired removal at end
    if last_was_minus and last_minus_content is not None and last_minus_line_num is not None:
        changes.append((last_minus_content, None, last_minus_line_num, None))
    
    return changes


def diff_archives(
    original_path: Path,
    modded_path: Path,
    extensions: Sequence[str],
    context: int,
    include_diff: bool = True,
    max_text_bytes: int = 1_000_000,
) -> List[FileDiff]:
    """Compute differences between two PAK/ZIP archives."""
    diffs: List[FileDiff] = []
    with zipfile.ZipFile(original_path, "r") as zf_orig, zipfile.ZipFile(
        modded_path, "r"
    ) as zf_mod:
        orig_members = set(_filtered_members(zf_orig, extensions))
        mod_members = set(_filtered_members(zf_mod, extensions))

        added = sorted(mod_members - orig_members)
        removed = sorted(orig_members - mod_members)
        common = sorted(orig_members & mod_members)

        for path in added:
            diffs.append(FileDiff(path=path, kind="added"))
        for path in removed:
            diffs.append(FileDiff(path=path, kind="removed"))

        for path in common:
            orig_bytes = _read_zip_file(zf_orig, path)
            mod_bytes = _read_zip_file(zf_mod, path)

            if orig_bytes == mod_bytes:
                continue  # identical; skip noise

            orig_is_text = _is_text(orig_bytes)
            mod_is_text = _is_text(mod_bytes)

            if orig_is_text and mod_is_text:
                orig_text = _decode_text(orig_bytes).splitlines()
                mod_text = _decode_text(mod_bytes).splitlines()
                # Param-level summary
                orig_params = _parse_params(orig_text)
                mod_params = _parse_params(mod_text)
                param_changes: List[tuple[str, str, str]] = []
                for name, old_val in orig_params.items():
                    if name in mod_params and mod_params[name] != old_val:
                        param_changes.append((name, old_val, mod_params[name]))

                diff_str = None
                diff_truncated = False
                if include_diff:
                    if len(orig_bytes) <= max_text_bytes and len(mod_bytes) <= max_text_bytes:
                        diff_lines = difflib.unified_diff(
                            orig_text,
                            mod_text,
                            fromfile=f"original/{path}",
                            tofile=f"modded/{path}",
                            n=context,
                        )
                        diff_str = "\n".join(diff_lines)
                        changed_lines = _extract_changed_lines(diff_str)
                    else:
                        diff_truncated = True
                        changed_lines = None
                else:
                    changed_lines = None

                diffs.append(
                    FileDiff(
                        path=path,
                        kind="modified-text",
                        diff=diff_str,
                        param_changes=param_changes or None,
                        diff_truncated=diff_truncated,
                        changed_lines=changed_lines,
                    )
                )
            else:
                diffs.append(FileDiff(path=path, kind="modified-binary"))

    return diffs


def _print_report(diffs: Iterable[FileDiff]) -> None:
    """Pretty-print the differences to stdout."""
    added = [d for d in diffs if d.kind == "added"]
    removed = [d for d in diffs if d.kind == "removed"]
    modified_text = [d for d in diffs if d.kind == "modified-text"]
    modified_bin = [d for d in diffs if d.kind == "modified-binary"]

    print("=== Summary ===")
    print(f"Added: {len(added)}")
    print(f"Removed: {len(removed)}")
    print(f"Modified text: {len(modified_text)}")
    print(f"Modified binary: {len(modified_bin)}")
    print()

    if added:
        print("=== Added files ===")
        for d in added:
            print(d.path)
        print()

    if removed:
        print("=== Removed files ===")
        for d in removed:
            print(d.path)
        print()

    if modified_bin:
        print("=== Modified binary files (no diff shown) ===")
        for d in modified_bin:
            print(d.path)
        print()

    if modified_text:
        print("=== Modified text files (unified diff) ===")
        for d in modified_text:
            print(f"[{d.path}]")
            if d.param_changes:
                print("  Param changes:")
                for name, old, new in d.param_changes:
                    print(f"    {name}: {old} -> {new}")
            else:
                print("  Param changes: none detected")
            if d.diff_truncated:
                print("  Diff skipped (file too large).")
            print()
            print(d.diff or "")
            print()


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diff two PAK/ZIP archives.")
    parser.add_argument(
        "--original",
        "-o",
        required=True,
        type=Path,
        help="Path to the original PAK (e.g., data0.pak).",
    )
    parser.add_argument(
        "--modded",
        "-m",
        required=True,
        type=Path,
        help="Path to the modded PAK (e.g., data7.pak).",
    )
    parser.add_argument(
        "--extensions",
        "-e",
        nargs="*",
        default=[".scr", ".cfg", ".json", ".txt"],
        help="File extensions to include (default: .scr .cfg .json .txt).",
    )
    parser.add_argument(
        "--context",
        "-c",
        type=int,
        default=3,
        help="Number of context lines to show in diffs (default: 3).",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    if not args.original.exists():
        print(f"Original not found: {args.original}", file=sys.stderr)
        return 1
    if not args.modded.exists():
        print(f"Modded not found: {args.modded}", file=sys.stderr)
        return 1

    try:
        diffs = diff_archives(
            original_path=args.original,
            modded_path=args.modded,
            extensions=[ext.lower() for ext in args.extensions],
            context=args.context,
        )
    except zipfile.BadZipFile as exc:
        print(
            f"Failed to read one of the archives as ZIP/PAK: {exc}",
            file=sys.stderr,
        )
        return 1

    _print_report(diffs)
    return 0


if __name__ == "__main__":
    sys.exit(main())

