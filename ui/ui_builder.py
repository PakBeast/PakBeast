"""Main UI builder - coordinates all UI components."""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App

from .toolbar import build_toolbar
from editor.tab import build_editor_tab
from settings.ui import build_appearance_tab
from .help_tab import build_help_tab
from comparison.ui.comparison_tab import build_comparison_tab


def build_ui(app: 'App') -> None:
    """Build the main UI using CustomTkinter with professional layout."""
    # Build toolbar
    build_toolbar(app)
    
    # Main container with padding
    main_container = ctk.CTkFrame(app, fg_color="transparent")
    main_container.pack(fill="both", expand=True, padx=12, pady=(12, 0))
    
    # Enhanced tabview with better styling
    main_tabs = ctk.CTkTabview(
        main_container,
        corner_radius=12,
        border_width=1,
        border_color=("gray75", "gray25"),
        segmented_button_fg_color=("gray90", "gray20"),
        segmented_button_selected_color=("gray80", "gray30"),
        segmented_button_selected_hover_color=("gray75", "gray35"),
        segmented_button_unselected_color=("gray95", "gray15"),
        segmented_button_unselected_hover_color=("gray90", "gray20"),
    )
    main_tabs.pack(fill="both", expand=True, pady=(0, 12))
    
    # Tab 1: Editor (File Explorer + Preview + Search & Edits)
    editor_tab = main_tabs.add("Editor")
    build_editor_tab(app, editor_tab)
    
    # Tab 2: Comparison (adjacent to Editor for quick access)
    comparison_tab = main_tabs.add("Comparison")
    build_comparison_tab(app, comparison_tab)
    
    # Tab 3: Appearance
    colors_tab = main_tabs.add("Appearance")
    build_appearance_tab(app, colors_tab)
    
    # Tab 4: Help
    help_tab = main_tabs.add("Help")
    build_help_tab(app, help_tab)
    
    # Store tabview reference for switching tabs
    app.main_tabs = main_tabs
    
    # Simplified status bar at the bottom (just version and general app status)
    status_bar = ctk.CTkFrame(app, height=28, fg_color=("gray85", "gray18"), border_width=1, border_color=("gray70", "gray30"))
    status_bar.pack(side="bottom", fill="x", padx=0, pady=0)
    status_bar.pack_propagate(False)
    
    status_container = ctk.CTkFrame(status_bar, fg_color="transparent")
    status_container.pack(fill="both", expand=True, padx=12, pady=4)
    
    # Left: General app status (for operations that don't have their own indicator)
    app.status = ctk.StringVar(value="")
    status_label = ctk.CTkLabel(
        status_container,
        textvariable=app.status,
        font=ctk.CTkFont(size=10),
        anchor="w",
        text_color=("gray50", "gray70")
    )
    status_label.pack(side="left")
    
    # Right: Version
    version_label = ctk.CTkLabel(
        status_container,
        text="v1.8",
        font=ctk.CTkFont(size=10),
        text_color=("gray50", "gray60")
    )
    version_label.pack(side="right")
    
    # Helper function for backward compatibility (for operations that still use it)
    def update_status(message: str, color: str = "#4CAF50"):
        """Update general status message (backward compatibility)."""
        app.status.set(message)
    
    app._update_status = update_status
