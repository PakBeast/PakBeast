"""Diff tab UI for comparing baseline vs current pak files."""

from __future__ import annotations

import threading
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog
from typing import TYPE_CHECKING, List

from operations.diff_runner import run_diff, diff_file

if TYPE_CHECKING:
    from core.app import App


def _set_status(app: "App", message: str, color: str = "#4CAF50") -> None:
    if hasattr(app, "_update_status"):
        app._update_status(message, color)
    else:
        app.status.set(message)


def build_diff_tab(app: "App", parent) -> None:
    container = ctk.CTkFrame(parent, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=12, pady=12)

    # Info note about path matching and version mismatches - moved to top for better visibility
    info_frame = ctk.CTkFrame(container, fg_color=("gray90", "gray20"), corner_radius=6, border_width=1, border_color=("gray80", "gray30"))
    info_frame.pack(pady=(0, 12))
    info_text = (
        "• Files must have matching internal paths to compare. \n"
        "• Different game versions may show false positives (added/removed/renamed params). \n"
        "• Check 'Params' tab for actual value changes."
    )
    info_label = ctk.CTkLabel(
        info_frame,
        text=info_text,
        font=ctk.CTkFont(size=11),
        text_color=("gray40", "gray60"),
        anchor="center",
        justify="center",
    )
    info_label.pack(padx=12, pady=8)

    controls = ctk.CTkFrame(container, fg_color="transparent")
    controls.pack(fill="x", pady=(0, 8))

    # Baseline selector
    baseline_label = ctk.CTkLabel(
        controls,
        text="Original PAK:",
        font=ctk.CTkFont(size=12, weight="bold"),
    )
    baseline_label.pack(side="left", padx=(0, 8))

    baseline_var = ctk.StringVar(value="")
    baseline_entry = ctk.CTkEntry(
        controls,
        textvariable=baseline_var,
        width=320,
        placeholder_text="Select baseline (original) .pak",
    )
    baseline_entry.pack(side="left", padx=(0, 8))

    def pick_baseline():
        p = filedialog.askopenfilename(
            title="Select Original PAK",
            filetypes=[("PAK/ZIP", "*.pak *.zip"), ("All files", "*.*")]
        )
        if p:
            baseline_var.set(p)
            _set_status(app, f"Baseline selected: {Path(p).name}")

    pick_btn = ctk.CTkButton(
        controls,
        text="Set Original",
        command=pick_baseline,
        width=110,
        height=32,
    )
    pick_btn.pack(side="left", padx=(0, 12))

    # Extensions
    ext_label = ctk.CTkLabel(controls, text="Extensions:", font=ctk.CTkFont(size=12, weight="bold"))
    ext_label.pack(side="left", padx=(0, 6))
    ext_var = ctk.StringVar(value=".scr .cfg .json .txt")
    ext_entry = ctk.CTkEntry(controls, textvariable=ext_var, width=180)
    ext_entry.pack(side="left", padx=(0, 10))

    # Context lines
    ctx_label = ctk.CTkLabel(controls, text="Context:", font=ctk.CTkFont(size=12, weight="bold"))
    ctx_label.pack(side="left", padx=(0, 6))
    ctx_var = ctk.StringVar(value="3")
    ctx_entry = ctk.CTkEntry(controls, textvariable=ctx_var, width=50)
    ctx_entry.pack(side="left", padx=(0, 12))

    # Compare button
    compare_btn = ctk.CTkButton(
        controls,
        text="Compare",
        width=100,
        height=32,
        command=lambda: _run_compare(app, baseline_var, ext_var, ctx_var, results_list, diff_text, params_list, changed_list),
    )
    compare_btn.pack(side="left")

    # Results area
    body = ctk.CTkFrame(container, fg_color="transparent")
    body.pack(fill="both", expand=True, pady=(8, 0))

    summary_var = ctk.StringVar(value="No comparison run.")
    summary_label = ctk.CTkLabel(body, textvariable=summary_var, font=ctk.CTkFont(size=12))
    summary_label.pack(anchor="w", pady=(0, 8))

    split = ctk.CTkFrame(body, fg_color="transparent")
    split.pack(fill="both", expand=True)

    list_frame = ctk.CTkFrame(split, fg_color=("gray95", "gray18"), corner_radius=6)
    list_frame.pack(side="left", fill="both", expand=False, padx=(0, 8))
    list_frame.configure(width=380)
    list_frame.pack_propagate(False)

    results_list = ctk.CTkScrollableFrame(list_frame, fg_color="transparent")
    results_list.pack(fill="both", expand=True, padx=6, pady=6)

    detail_frame = ctk.CTkFrame(split, fg_color=("gray95", "gray18"), corner_radius=6)
    detail_frame.pack(side="left", fill="both", expand=True)

    tabview = ctk.CTkTabview(detail_frame)
    tabview.pack(fill="both", expand=True, padx=8, pady=8)

    tab_params = tabview.add("Params")
    params_list = ctk.CTkScrollableFrame(tab_params, fg_color="transparent")
    params_list.pack(fill="both", expand=True, padx=10, pady=10)

    tab_changed = tabview.add("Changed lines")
    changed_list = ctk.CTkScrollableFrame(tab_changed, fg_color="transparent")
    changed_list.pack(fill="both", expand=True, padx=10, pady=10)

    tab_diff = tabview.add("Diff")
    diff_text = ctk.CTkTextbox(tab_diff)
    diff_text.pack(fill="both", expand=True, padx=10, pady=10)
    diff_text.configure(state="disabled")

    def set_summary(text: str):
        summary_var.set(text)

    app.set_diff_summary = set_summary


def _run_compare(app: "App", baseline_var, ext_var, ctx_var, results_list, diff_text, params_list, changed_list):
    from pathlib import Path

    baseline = baseline_var.get().strip()
    current = str(app.current_pak_path) if app.current_pak_path else ""

    if not baseline or not Path(baseline).exists():
        _set_status(app, "Select a valid baseline pak first", "#E53935")
        return
    if not current or not Path(current).exists():
        _set_status(app, "Load a pak to compare against baseline", "#E53935")
        return

    try:
        context = max(0, int(ctx_var.get()))
    except ValueError:
        context = 3
        ctx_var.set("3")

    extensions: List[str] = [e if e.startswith(".") else f".{e}" for e in ext_var.get().split() if e]

    _set_status(app, "Comparing...", "#2196F3")

    def worker():
        try:
            diffs, summary = run_diff(
                original_path=Path(baseline),
                modded_path=Path(current),
                extensions=extensions,
                context=context,
                include_diff=False,  # lazy load per file to keep UI fast
                max_text_bytes=1_000_000,
            )
        except Exception as exc:
            app.after(0, lambda: _set_status(app, f"Diff failed: {exc}", "#E53935"))
            return

        def update_ui():
            _set_status(app, "Diff complete", "#4CAF50")
            # Focus on changes we show (added + modified); omit removed in display
            filtered = [d for d in diffs if d.kind != "removed"]
            summary_display = (
                f"Shown — Added: {summary['added']} • Modified text: {summary['modified_text']} • Modified binary: {summary['modified_binary']}"
            )
            app.set_diff_summary(summary_display)
            _populate_results_list(
                app,
                results_list,
                filtered,
                diff_text,
                params_list,
                Path(baseline),
                Path(current),
                context,
                changed_list,
            )

        app.after(0, update_ui)

    threading.Thread(target=worker, daemon=True).start()


def _populate_results_list(app: "App", frame: ctk.CTkScrollableFrame, diffs, diff_text, params_list, baseline_path: Path, current_path: Path, context: int, changed_list):
    for child in frame.winfo_children():
        child.destroy()
    MAX_ITEMS = 400  # safety cap to keep UI responsive
    shown = 0
    for d in diffs:
        if shown >= MAX_ITEMS:
            break
        row = ctk.CTkFrame(frame, fg_color=("gray90", "gray16"), corner_radius=4)
        row.pack(fill="x", padx=4, pady=2)
        kind_color = {
            "added": "#43A047",
            "removed": "#E53935",
            "modified-text": "#FB8C00",
            "modified-binary": "#8E24AA",
        }.get(d.kind, "#90A4AE")
        badge = ctk.CTkLabel(row, text=d.kind, text_color=kind_color, font=ctk.CTkFont(size=11, weight="bold"))
        badge.pack(side="left", padx=6, pady=4)
        label = ctk.CTkButton(
            row,
            text=d.path,
            fg_color="transparent",
            hover_color=("gray80", "gray25"),
            text_color=("black", "white"),
            anchor="w",
            command=lambda diff=d: _show_diff(diff, diff_text, params_list, baseline_path, current_path, context, changed_list),
        )
        label.pack(side="left", fill="x", expand=True, padx=(4, 8))
        shown += 1
    remaining = len(diffs) - shown
    if remaining > 0:
        note = ctk.CTkLabel(
            frame,
            text=f"... {remaining} more entries not shown to keep UI responsive",
            text_color="#90A4AE",
            font=ctk.CTkFont(size=11, slant="italic"),
            anchor="w",
        )
        note.pack(fill="x", padx=8, pady=6)


def _populate_changed_lines(changed_list: ctk.CTkScrollableFrame, changed_lines):
    """Helper to populate the changed lines list with line numbers."""
    for child in changed_list.winfo_children():
        child.destroy()
    if changed_lines:
        MAX_CHANGED = 200
        count = 0
        for item in changed_lines:
            if count >= MAX_CHANGED:
                break
            # Handle both old format (2-tuple) and new format (4-tuple with line numbers)
            if len(item) == 4:
                old_line, new_line, old_line_num, new_line_num = item
            else:
                old_line, new_line = item
                old_line_num, new_line_num = None, None
            
            row = ctk.CTkFrame(changed_list, fg_color="transparent")
            row.pack(fill="x", padx=4, pady=1)
            
            if old_line is not None and new_line is not None:
                # Changed line - show both with line numbers
                line_info = ""
                if old_line_num is not None and new_line_num is not None:
                    line_info = f"Line {old_line_num} → {new_line_num}: "
                elif old_line_num is not None:
                    line_info = f"Line {old_line_num} → ?: "
                elif new_line_num is not None:
                    line_info = f"Line ? → {new_line_num}: "
                
                if line_info:
                    ctk.CTkLabel(row, text=line_info, text_color="#90A4AE", font=ctk.CTkFont(size=10, weight="bold"), anchor="w", width=120).pack(side="left", padx=(0, 4))
                ctk.CTkLabel(row, text=old_line, text_color="#e57373", anchor="w").pack(anchor="w")
                ctk.CTkLabel(row, text=new_line, text_color="#81c784", anchor="w").pack(anchor="w", pady=(0, 4))
            elif old_line is not None:
                # Removed line
                line_info = f"Line {old_line_num}:" if old_line_num is not None else ""
                if line_info:
                    ctk.CTkLabel(row, text=line_info, text_color="#90A4AE", font=ctk.CTkFont(size=10, weight="bold"), anchor="w", width=120).pack(side="left", padx=(0, 4))
                ctk.CTkLabel(row, text=old_line, text_color="#e57373", anchor="w").pack(anchor="w")
            elif new_line is not None:
                # Added line
                line_info = f"Line {new_line_num}:" if new_line_num is not None else ""
                if line_info:
                    ctk.CTkLabel(row, text=line_info, text_color="#90A4AE", font=ctk.CTkFont(size=10, weight="bold"), anchor="w", width=120).pack(side="left", padx=(0, 4))
                ctk.CTkLabel(row, text=new_line, text_color="#81c784", anchor="w").pack(anchor="w")
            count += 1
        if len(changed_lines) > MAX_CHANGED:
            note = ctk.CTkLabel(changed_list, text=f"... {len(changed_lines) - MAX_CHANGED} more changes not shown", text_color="#90A4AE", font=ctk.CTkFont(size=11))
            note.pack(anchor="w", padx=4, pady=2)
    else:
        row = ctk.CTkFrame(changed_list, fg_color="transparent")
        row.pack(fill="x", padx=4, pady=1)
        ctk.CTkLabel(row, text="No changed lines detected").pack(anchor="w")


def _show_diff(diff, diff_text: ctk.CTkTextbox, params_list: ctk.CTkScrollableFrame, baseline_path: Path, current_path: Path, context: int, changed_list: ctk.CTkScrollableFrame):
    # Refresh diff data if needed (lazy loading for performance)
    if diff.diff is None or diff.changed_lines is None:
        refreshed = diff_file(baseline_path, current_path, diff.path, context, max_text_bytes=1_000_000)
        diff.diff = refreshed.diff
        diff.param_changes = refreshed.param_changes
        diff.diff_truncated = refreshed.diff_truncated
        diff.changed_lines = refreshed.changed_lines

    # Populate param changes
    for child in params_list.winfo_children():
        child.destroy()
    if diff.param_changes:
        for name, old, new in diff.param_changes:
            row = ctk.CTkFrame(params_list, fg_color="transparent")
            row.pack(fill="x", padx=4, pady=6)
            ctk.CTkLabel(row, text=name, width=200, anchor="w").pack(side="left", padx=(0, 12))
            ctk.CTkLabel(row, text=f"{old} → {new}", anchor="w").pack(side="left", padx=(0, 8))
    else:
        row = ctk.CTkFrame(params_list, fg_color="transparent")
        row.pack(fill="x", padx=4, pady=1)
        ctk.CTkLabel(row, text="No param changes detected").pack(anchor="w")

    # Populate changed lines
    _populate_changed_lines(changed_list, diff.changed_lines)

    # Populate diff text
    diff_text.configure(state="normal")
    diff_text.delete("1.0", "end")
    if diff.diff_truncated:
        diff_text.insert("1.0", "[Diff skipped: file too large for in-app view]\n")
    diff_text.insert("1.0", diff.diff or "[No diff text]")
    diff_text.configure(state="disabled")

