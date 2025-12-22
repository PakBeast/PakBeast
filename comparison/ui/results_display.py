"""Results display area UI builder for comparison tab."""

import customtkinter as ctk
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from core.app import App


def build_results_area(app: "App", parent: ctk.CTkFrame) -> Dict:
    """Build the results display area (summary with file names, info panel, detail tabs)."""
    # Results area
    body = ctk.CTkFrame(parent, fg_color="transparent")
    body.pack(fill="both", expand=True, pady=(8, 0))

    # Summary area with file names
    summary_frame = ctk.CTkFrame(body, fg_color="transparent")
    summary_frame.pack(fill="x", pady=(0, 10))
    
    # Results text
    summary_var = ctk.StringVar(value="No comparison run.")
    summary_label = ctk.CTkLabel(
        summary_frame,
        textvariable=summary_var,
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=("gray10", "gray90"),
    )
    summary_label.pack(side="left", padx=(0, 20))
    
    # File names display
    files_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
    files_frame.pack(side="left", fill="x", expand=True)
    
    original_file_var = ctk.StringVar(value="")
    modded_file_var = ctk.StringVar(value="")
    
    original_label = ctk.CTkLabel(
        files_frame,
        textvariable=original_file_var,
        font=ctk.CTkFont(size=11),
        text_color=("#e57373", "#e57373"),
        anchor="w",
    )
    original_label.pack(side="left", padx=(0, 15))
    
    modded_label = ctk.CTkLabel(
        files_frame,
        textvariable=modded_file_var,
        font=ctk.CTkFont(size=11),
        text_color=("#81c784", "#81c784"),
        anchor="w",
    )
    modded_label.pack(side="left")

    split = ctk.CTkFrame(body, fg_color="transparent")
    split.pack(fill="both", expand=True)

    # Left side: Info panel (replaces file list)
    info_panel = ctk.CTkFrame(
        split,
        fg_color=("gray98", "gray18"),
        corner_radius=10,
        border_width=1,
        border_color=("gray80", "gray25"),
    )
    info_panel.pack(side="left", fill="both", expand=False, padx=(0, 12))
    info_panel.configure(width=300)
    info_panel.pack_propagate(False)

    # Info panel header
    info_header = ctk.CTkLabel(
        info_panel,
        text="ℹ️ Comparison Info",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=("gray10", "gray90"),
    )
    info_header.pack(padx=10, pady=(10, 8), anchor="w")
    
    # Info content area
    info_content = ctk.CTkScrollableFrame(info_panel, fg_color="transparent")
    info_content.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    # Placeholder for results list (kept for compatibility but won't be used)
    results_list = ctk.CTkScrollableFrame(info_panel, fg_color="transparent")

    detail_frame = ctk.CTkFrame(
        split,
        fg_color=("gray98", "gray18"),
        corner_radius=10,
        border_width=1,
        border_color=("gray80", "gray25"),
    )
    detail_frame.pack(side="left", fill="both", expand=True)

    # Enhanced tabview styling
    tabview = ctk.CTkTabview(
        detail_frame,
        corner_radius=8,
        border_width=1,
        border_color=("gray75", "gray25"),
        segmented_button_fg_color=("gray90", "gray20"),
        segmented_button_selected_color=("gray80", "gray30"),
        segmented_button_selected_hover_color=("gray75", "gray35"),
        segmented_button_unselected_color=("gray95", "gray15"),
        segmented_button_unselected_hover_color=("gray90", "gray20"),
    )
    tabview.pack(fill="both", expand=True, padx=10, pady=10)

    # Changes tab (renamed from Params) - shows key changes in an eye-catching way
    tab_changes = tabview.add("Changes")
    changes_list = ctk.CTkScrollableFrame(tab_changes, fg_color="transparent")
    changes_list.pack(fill="both", expand=True, padx=10, pady=10)

    # Full Text tab - shows raw line-by-line differences
    tab_full_text = tabview.add("Full Text")
    diff_text = ctk.CTkTextbox(tab_full_text)
    diff_text.pack(fill="both", expand=True, padx=10, pady=10)
    diff_text.configure(state="disabled")

    # Store all comparisons - need to be accessible in comparison runner
    all_diffs_storage = {
        "diffs": [],
        "baseline_path": None,
        "current_path": None,
        "context": 3,
        "diff_text": diff_text,
        "params_list": changes_list,
        "info_content": info_content,
    }
    
    def set_summary(text: str, orig_name: str = "", mod_name: str = ""):
        summary_var.set(text)
        if orig_name:
            original_file_var.set(f"➖ {orig_name}")
        else:
            original_file_var.set("")
        if mod_name:
            modded_file_var.set(f"➕ {mod_name}")
        else:
            modded_file_var.set("")

    app.set_comparison_summary = set_summary
    
    return {
        "results_list": results_list,
        "diff_text": diff_text,
        "params_list": changes_list,
        "storage": all_diffs_storage,
    }
