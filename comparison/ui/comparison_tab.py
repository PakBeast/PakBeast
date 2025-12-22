"""Main comparison tab builder."""

from __future__ import annotations

from pathlib import Path
import customtkinter as ctk
from typing import TYPE_CHECKING

from ..operations.comparison_runner import run_comparison, parse_file_path
from .controls import build_controls
from .results_display import build_results_area
from .info_panel import populate_info_panel
from .changes_viewer import populate_changes_viewer
from .text_viewer import populate_text_viewer

if TYPE_CHECKING:
    from core.app import App


def _set_status(app: "App", message: str, color: str = "#4CAF50") -> None:
    """Helper to set status message."""
    if hasattr(app, "_update_status"):
        app._update_status(message, color)
    else:
        app.status.set(message)


def build_comparison_tab(app: "App", parent) -> None:
    """Build the comparison tab UI."""
    container = ctk.CTkFrame(parent, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=12, pady=12)

    # Info note about using exported TXT files
    info_frame = ctk.CTkFrame(
        container,
        fg_color=("gray95", "gray20"),
        corner_radius=8,
        border_width=1,
        border_color=("gray85", "gray30")
    )
    info_frame.pack(fill="x", padx=0, pady=(0, 12))
    info_text = (
        "• Compare TXT files for reliable results. \n"
        "• Select one original TXT file and one modded TXT file to compare."
    )
    info_label = ctk.CTkLabel(
        info_frame,
        text=info_text,
        font=ctk.CTkFont(size=11),
        text_color=("gray30", "gray80"),
        anchor="center",
        justify="center",
    )
    info_label.pack(padx=14, pady=10)

    # Build controls and results area
    controls_data = build_controls(app, container)
    results_data = build_results_area(app, container)
    
    # Combine data for callback functions
    all_diffs_storage = results_data["storage"]
    all_diffs_storage.update({
        "original_var": controls_data["original_var"],
        "modded_var": controls_data["modded_var"],
        "ctx_var": controls_data["ctx_var"],
    })
    
    def handle_compare():
        """Handle compare button click."""
        original_str = controls_data["original_var"].get().strip()
        modded_str = controls_data["modded_var"].get().strip()

        if not original_str:
            _set_status(app, "Select an original TXT file", "#E53935")
            return
        if not modded_str:
            _set_status(app, "Select a modded TXT file", "#E53935")
            return

        original_path = parse_file_path(original_str)
        modded_path = parse_file_path(modded_str)

        if not original_path:
            _set_status(app, "Original file not found", "#E53935")
            return
        if not modded_path:
            _set_status(app, "Modded file not found", "#E53935")
            return

        try:
            context = max(0, int(controls_data["ctx_var"].get()))
        except ValueError:
            context = 3
            controls_data["ctx_var"].set("3")

        _set_status(app, "Comparing TXT files...", "#2196F3")

        def on_complete(file_diffs, summary):
            """Handle successful comparison."""
            _set_status(app, "Comparison complete", "#4CAF50")
            # Show all comparisons (modified files)
            filtered = [d for d in file_diffs if d.kind in ("modified-text", "modified-binary")]
            
            # Build summary with file names
            summary_display = (
                f"Results — Modified text: {summary['modified_text']} • Modified binary: {summary['modified_binary']}"
            )
            if summary['added'] > 0 or summary['removed'] > 0:
                summary_display += f" • Added: {summary['added']} • Removed: {summary['removed']}"
            
            # Store file names for display in summary
            all_diffs_storage["original_file"] = original_path
            all_diffs_storage["modded_file"] = modded_path
            
            app.set_comparison_summary(summary_display, original_path.name, modded_path.name)
            
            # Store all comparisons
            all_diffs_storage["diffs"] = filtered
            all_diffs_storage["baseline_path"] = original_path
            all_diffs_storage["current_path"] = modded_path
            all_diffs_storage["context"] = context
            
            # Show results directly
            if filtered:
                # Show the first (and only) comparison result
                diff = filtered[0]
                populate_changes_viewer(
                    results_data["params_list"],
                    diff,
                )
                populate_text_viewer(
                    results_data["diff_text"],
                    diff,
                    original_path,
                    modded_path,
                    context,
                )
                # Populate info panel
                populate_info_panel(
                    all_diffs_storage["info_content"],
                    diff,
                    original_path,
                    modded_path,
                )

        def on_error(error_msg: str):
            """Handle comparison error."""
            _set_status(app, f"Comparison failed: {error_msg}", "#E53935")

        # Run comparison in background thread
        run_comparison(
            app,
            original_path,
            modded_path,
            context,
            on_complete,
            on_error,
        )
    
    # Connect compare button
    controls_data["compare_btn"].configure(command=handle_compare)
