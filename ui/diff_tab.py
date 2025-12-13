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
        text="Original:",
        font=ctk.CTkFont(size=12, weight="bold"),
    )
    baseline_label.pack(side="left", padx=(0, 8))

    baseline_var = ctk.StringVar(value="")
    baseline_entry = ctk.CTkEntry(
        controls,
        textvariable=baseline_var,
        width=320,
        placeholder_text="Select baseline (original) file",
    )
    baseline_entry.pack(side="left", padx=(0, 8))

    def pick_baseline():
        p = filedialog.askopenfilename(
            title="Select Original PAK or Text File",
            filetypes=[("PAK/ZIP", "*.pak *.zip"), ("Text files", "*.txt *.loot *.scr *.cfg *.json"), ("All files", "*.*")]
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

    # Modded selector (optional - falls back to current_pak_path)
    modded_label = ctk.CTkLabel(
        controls,
        text="Modded:",
        font=ctk.CTkFont(size=12, weight="bold"),
    )
    modded_label.pack(side="left", padx=(0, 8))

    modded_var = ctk.StringVar(value="")
    modded_entry = ctk.CTkEntry(
        controls,
        textvariable=modded_var,
        width=320,
        placeholder_text="Select modded file (or use loaded PAK)",
    )
    modded_entry.pack(side="left", padx=(0, 8))

    def pick_modded():
        p = filedialog.askopenfilename(
            title="Select Modded PAK or Text File",
            filetypes=[("PAK/ZIP", "*.pak *.zip"), ("Text files", "*.txt *.loot *.scr *.cfg *.json"), ("All files", "*.*")]
        )
        if p:
            modded_var.set(p)
            _set_status(app, f"Modded file selected: {Path(p).name}")

    pick_modded_btn = ctk.CTkButton(
        controls,
        text="Set Modded",
        command=pick_modded,
        width=110,
        height=32,
    )
    pick_modded_btn.pack(side="left", padx=(0, 12))

    # Extensions
    ext_label = ctk.CTkLabel(controls, text="Extensions:", font=ctk.CTkFont(size=12, weight="bold"))
    ext_label.pack(side="left", padx=(0, 6))
    ext_var = ctk.StringVar(value=".scr .cfg .json .txt .loot")
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
        command=lambda: _run_compare(app, baseline_var, modded_var, ext_var, ctx_var, results_list, diff_text, params_list, filter_var, all_diffs_storage, apply_filter),
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

    # Filter/search box for results
    filter_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
    filter_frame.pack(fill="x", padx=6, pady=(6, 4))
    
    filter_label = ctk.CTkLabel(
        filter_frame,
        text="Filter:",
        font=ctk.CTkFont(size=11, weight="bold"),
    )
    filter_label.pack(side="left", padx=(0, 6))
    
    filter_var = ctk.StringVar(value="")
    filter_entry = ctk.CTkEntry(
        filter_frame,
        textvariable=filter_var,
        placeholder_text="Filter by file path/name...",
        width=300,
    )
    filter_entry.pack(side="left", fill="x", expand=True)
    
    clear_filter_btn = ctk.CTkButton(
        filter_frame,
        text="✕",
        width=30,
        height=24,
        command=lambda: filter_var.set(""),
        font=ctk.CTkFont(size=12),
    )
    clear_filter_btn.pack(side="left", padx=(4, 0))

    results_list = ctk.CTkScrollableFrame(list_frame, fg_color="transparent")
    results_list.pack(fill="both", expand=True, padx=6, pady=(0, 6))

    detail_frame = ctk.CTkFrame(split, fg_color=("gray95", "gray18"), corner_radius=6)
    detail_frame.pack(side="left", fill="both", expand=True)

    tabview = ctk.CTkTabview(detail_frame)
    tabview.pack(fill="both", expand=True, padx=8, pady=8)

    tab_params = tabview.add("Params")
    params_list = ctk.CTkScrollableFrame(tab_params, fg_color="transparent")
    params_list.pack(fill="both", expand=True, padx=10, pady=10)

    tab_diff = tabview.add("Diff")
    diff_text = ctk.CTkTextbox(tab_diff)
    diff_text.pack(fill="both", expand=True, padx=10, pady=10)
    diff_text.configure(state="disabled")

    # Store all diffs and filter function - need to be accessible in _run_compare
    all_diffs_storage = {"diffs": [], "baseline_path": None, "current_path": None, "context": 3, "diff_text": diff_text, "params_list": params_list}
    
    def apply_filter():
        """Apply filter to the results list."""
        filter_text = filter_var.get().lower().strip()
        if filter_text:
            filtered = [d for d in all_diffs_storage["diffs"] if filter_text in d.path.lower()]
            # Update summary to show filtered count
            if hasattr(app, 'set_diff_summary') and all_diffs_storage["diffs"]:
                total = len(all_diffs_storage["diffs"])
                shown = len(filtered)
                if shown < total:
                    app.set_diff_summary(f"Showing {shown} of {total} results (filtered)")
                else:
                    app.set_diff_summary(f"Shown — Added: {sum(1 for d in all_diffs_storage['diffs'] if d.kind == 'added')} • Modified text: {sum(1 for d in all_diffs_storage['diffs'] if d.kind == 'modified-text')} • Modified binary: {sum(1 for d in all_diffs_storage['diffs'] if d.kind == 'modified-binary')}")
        else:
            filtered = all_diffs_storage["diffs"]
        
        _populate_results_list(
            app,
            results_list,
            filtered,
            all_diffs_storage["diff_text"],
            all_diffs_storage["params_list"],
            all_diffs_storage["baseline_path"],
            all_diffs_storage["current_path"],
            all_diffs_storage["context"],
        )
    
    filter_var.trace_add("write", lambda *args: apply_filter())

    def set_summary(text: str):
        summary_var.set(text)

    app.set_diff_summary = set_summary


def _run_compare(app: "App", baseline_var, modded_var, ext_var, ctx_var, results_list, diff_text, params_list, filter_var, all_diffs_storage, apply_filter):
    from pathlib import Path

    baseline = baseline_var.get().strip()
    modded = modded_var.get().strip()
    # Fall back to current_pak_path if modded not specified
    if not modded:
        modded = str(app.current_pak_path) if app.current_pak_path else ""

    if not baseline or not Path(baseline).exists():
        _set_status(app, "Select a valid baseline file first", "#E53935")
        return
    if not modded or not Path(modded).exists():
        _set_status(app, "Select a modded file or load a pak to compare against baseline", "#E53935")
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
                modded_path=Path(modded),
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
            
            # Store all diffs for filtering
            all_diffs_storage["diffs"] = filtered
            all_diffs_storage["baseline_path"] = Path(baseline)
            all_diffs_storage["current_path"] = Path(modded)
            all_diffs_storage["context"] = context
            all_diffs_storage["diff_text"] = diff_text
            all_diffs_storage["params_list"] = params_list
            
            # Apply current filter (if any)
            apply_filter()

        app.after(0, update_ui)

    threading.Thread(target=worker, daemon=True).start()


def _populate_results_list(app: "App", frame: ctk.CTkScrollableFrame, diffs, diff_text, params_list, baseline_path: Path, current_path: Path, context: int):
    for child in frame.winfo_children():
        child.destroy()
    MAX_ITEMS = 400  # safety cap to keep UI responsive
    shown = 0
    for d in diffs:
        if shown >= MAX_ITEMS:
            break
        row = ctk.CTkFrame(frame, fg_color=("gray90", "gray16"), corner_radius=4)
        row.pack(fill="x", padx=4, pady=2)
        kind_info = {
            "added": ("➕ ADDED", "#43A047"),
            "removed": ("➖ REMOVED", "#E53935"),
            "modified-text": ("✏️ MODIFIED", "#FB8C00"),
            "modified-binary": ("🔷 BINARY", "#8E24AA"),
        }.get(d.kind, ("❓ UNKNOWN", "#90A4AE"))
        
        badge_text, kind_color = kind_info
        badge = ctk.CTkLabel(row, text=badge_text, text_color=kind_color, font=ctk.CTkFont(size=10, weight="bold"))
        badge.pack(side="left", padx=6, pady=4)
        label = ctk.CTkButton(
            row,
            text=d.path,
            fg_color="transparent",
            hover_color=("gray80", "gray25"),
            text_color=("black", "white"),
            anchor="w",
            command=lambda diff=d: _show_diff(diff, diff_text, params_list, baseline_path, current_path, context),
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


def _show_diff(diff, diff_text: ctk.CTkTextbox, params_list: ctk.CTkScrollableFrame, baseline_path: Path, current_path: Path, context: int):
    # Refresh diff data if needed (lazy loading for performance)
    if diff.diff is None:
        refreshed = diff_file(baseline_path, current_path, diff.path, context, max_text_bytes=1_000_000)
        diff.diff = refreshed.diff
        diff.param_changes = refreshed.param_changes
        diff.diff_truncated = refreshed.diff_truncated
        diff.changed_lines = refreshed.changed_lines

    # Populate param changes
    for child in params_list.winfo_children():
        child.destroy()
    if diff.param_changes:
        # Summary header
        summary_frame = ctk.CTkFrame(params_list, fg_color=("gray95", "gray20"), corner_radius=4)
        summary_frame.pack(fill="x", padx=4, pady=(0, 8))
        summary_label = ctk.CTkLabel(
            summary_frame,
            text=f"📋 {len(diff.param_changes)} parameter change(s)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray50", "gray70"),
        )
        summary_label.pack(padx=8, pady=6)
        
        for name, old, new in diff.param_changes:
            param_container = ctk.CTkFrame(params_list, fg_color=("gray98", "gray15"), corner_radius=4)
            param_container.pack(fill="x", padx=4, pady=3)
            
            # Parameter name header
            name_frame = ctk.CTkFrame(param_container, fg_color="transparent")
            name_frame.pack(fill="x", padx=6, pady=(6, 4))
            name_label = ctk.CTkLabel(
                name_frame,
                text=f"🔧 {name}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("black", "white"),
            )
            name_label.pack(side="left")
            
            # Old value
            old_frame = ctk.CTkFrame(param_container, fg_color=("gray95", "gray18"), corner_radius=3)
            old_frame.pack(fill="x", padx=6, pady=(0, 4))
            old_label = ctk.CTkLabel(
                old_frame,
                text=f"➖ OLD: {old}",
                text_color="#e57373",
                font=ctk.CTkFont(size=10),
                anchor="w",
            )
            old_label.pack(fill="x", padx=6, pady=4)
            
            # New value
            new_frame = ctk.CTkFrame(param_container, fg_color=("gray95", "gray18"), corner_radius=3)
            new_frame.pack(fill="x", padx=6, pady=(0, 6))
            new_label = ctk.CTkLabel(
                new_frame,
                text=f"➕ NEW: {new}",
                text_color="#81c784",
                font=ctk.CTkFont(size=10),
                anchor="w",
            )
            new_label.pack(fill="x", padx=6, pady=4)
    else:
        row = ctk.CTkFrame(params_list, fg_color="transparent")
        row.pack(fill="x", padx=4, pady=8)
        no_params_label = ctk.CTkLabel(
            row,
            text="✓ No parameter changes detected",
            text_color="#90A4AE",
            font=ctk.CTkFont(size=11),
        )
        no_params_label.pack(anchor="w")

    # Populate diff text
    diff_text.configure(state="normal")
    diff_text.delete("1.0", "end")
    if diff.diff_truncated:
        diff_text.insert("1.0", "[Diff skipped: file too large for in-app view]\n")
    diff_text.insert("1.0", diff.diff or "[No diff text]")
    diff_text.configure(state="disabled")

