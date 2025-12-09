"""Editor tab builder that delegates to subcomponents."""

import customtkinter as ctk
from typing import TYPE_CHECKING

from .editor.config import EDIT_TYPE_FILTER_LAYOUT
from .editor.edits_panel import build_edits_panel
from .editor.file_explorer import build_file_explorer
from .editor.preview_panel import build_preview_panel
from .editor.search_panel import build_search_panel

if TYPE_CHECKING:
    from core.app import App


def build_editor_tab(app: "App", parent):
    """Build the editor tab with left sidebar tabs and right preview panel."""
    editor_container = ctk.CTkFrame(parent, fg_color="transparent")
    editor_container.pack(fill="both", expand=True, padx=8, pady=8)

    left_sidebar = ctk.CTkFrame(editor_container, fg_color="transparent")
    left_sidebar.pack(side="left", fill="both", expand=False, padx=(0, 12))
    left_sidebar.configure(width=650)
    left_sidebar.pack_propagate(False)

    sidebar_tabs = ctk.CTkTabview(left_sidebar)
    sidebar_tabs.pack(fill="both", expand=True)

    files_tab = sidebar_tabs.add("Files")
    explorer_panel = ctk.CTkFrame(
        files_tab,
        fg_color="transparent",
        border_width=1,
        border_color=("gray70", "gray30"),
        corner_radius=8,
    )
    explorer_panel.pack(fill="both", expand=True)
    build_file_explorer(app, explorer_panel)

    search_edits_tab = sidebar_tabs.add("Search & Modifications")

    search_panel = ctk.CTkFrame(
        search_edits_tab,
        fg_color="transparent",
        border_width=1,
        border_color=("gray70", "gray30"),
        corner_radius=8,
    )
    search_panel.pack(fill="both", expand=True, pady=(0, 8))
    build_search_panel(app, search_panel)

    edits_panel = ctk.CTkFrame(
        search_edits_tab,
        fg_color="transparent",
        border_width=1,
        border_color=("gray70", "gray30"),
        corner_radius=8,
    )
    edits_panel.pack(fill="both", expand=True)
    build_edits_panel(app, edits_panel)

    preview_panel = ctk.CTkFrame(
        editor_container,
        fg_color="transparent",
        border_width=1,
        border_color=("gray70", "gray30"),
        corner_radius=8,
    )
    preview_panel.pack(side="left", fill="both", expand=True)
    build_preview_panel(app, preview_panel)


__all__ = [
    "build_editor_tab",
    "EDIT_TYPE_FILTER_LAYOUT",
]

