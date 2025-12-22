"""Editor tab builder that delegates to subcomponents."""

import customtkinter as ctk
from typing import TYPE_CHECKING

from .ui.config import EDIT_TYPE_FILTER_LAYOUT
from .ui.edits_panel import build_edits_panel
from .ui.file_explorer import build_file_explorer
from .ui.preview_panel import build_preview_panel
from .ui.search_panel import build_search_panel

if TYPE_CHECKING:
    from core.app import App


def build_editor_tab(app: "App", parent):
    """Build the editor tab with tabs on left, preview always visible on right."""
    # Main container with refined spacing
    editor_container = ctk.CTkFrame(parent, fg_color="transparent")
    editor_container.pack(fill="both", expand=True, padx=12, pady=12)

    # Left side: Tabbed sidebar (Files | Modifications) - 30% of width
    left_sidebar = ctk.CTkFrame(editor_container, fg_color="transparent")
    left_sidebar.pack(side="left", fill="both", expand=False, padx=(0, 16))
    left_sidebar.configure(width=480)  # ~30% of typical 1600px window width
    left_sidebar.pack_propagate(False)

    # Enhanced tabview with better styling
    sidebar_tabs = ctk.CTkTabview(
        left_sidebar,
        corner_radius=12,
        border_width=1,
        border_color=("gray75", "gray25"),
        segmented_button_fg_color=("gray90", "gray20"),
        segmented_button_selected_color=("gray80", "gray30"),
        segmented_button_selected_hover_color=("gray75", "gray35"),
        segmented_button_unselected_color=("gray95", "gray15"),
        segmented_button_unselected_hover_color=("gray90", "gray20"),
    )
    sidebar_tabs.pack(fill="both", expand=True)

    # Files tab
    files_tab = sidebar_tabs.add("Files")
    explorer_panel = ctk.CTkFrame(
        files_tab,
        fg_color=("gray98", "gray18"),
        border_width=1,
        border_color=("gray80", "gray25"),
        corner_radius=10,
    )
    explorer_panel.pack(fill="both", expand=True, padx=10, pady=10)
    build_file_explorer(app, explorer_panel)

    # Modifications tab (Search + Edits stacked with equal heights)
    modifications_tab = sidebar_tabs.add("Modifications")
    
    # Container for equal height distribution using grid
    modifications_container = ctk.CTkFrame(modifications_tab, fg_color="transparent")
    modifications_container.pack(fill="both", expand=True, padx=10, pady=10)
    modifications_container.grid_rowconfigure(0, weight=1)
    modifications_container.grid_rowconfigure(1, weight=1)
    modifications_container.grid_columnconfigure(0, weight=1)
    
    # Search panel (top of modifications tab) - enhanced styling, 50% height
    search_panel = ctk.CTkFrame(
        modifications_container,
        fg_color=("gray98", "gray18"),
        border_width=1,
        border_color=("gray80", "gray25"),
        corner_radius=10,
    )
    search_panel.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 8))
    build_search_panel(app, search_panel)
    
    # Edits panel (bottom of modifications tab) - enhanced styling, 50% height
    edits_panel = ctk.CTkFrame(
        modifications_container,
        fg_color=("gray98", "gray18"),
        border_width=1,
        border_color=("gray80", "gray25"),
        corner_radius=10,
    )
    edits_panel.grid(row=1, column=0, sticky="nsew", padx=0, pady=(0, 0))
    build_edits_panel(app, edits_panel)

    # Right side: Preview panel (always visible, takes remaining ~70% space) - enhanced styling
    preview_panel = ctk.CTkFrame(
        editor_container,
        fg_color=("gray98", "gray18"),
        border_width=1,
        border_color=("gray80", "gray25"),
        corner_radius=10,
    )
    preview_panel.pack(side="left", fill="both", expand=True)
    build_preview_panel(app, preview_panel)


__all__ = [
    "build_editor_tab",
    "EDIT_TYPE_FILTER_LAYOUT",
]

