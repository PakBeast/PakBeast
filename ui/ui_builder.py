"""Main UI builder - coordinates all UI components."""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App

from .toolbar import build_toolbar
from .editor_tab import build_editor_tab
from .settings_tabs import build_general_settings_tab, build_multi_packer_tab, build_colors_tab
from .help_tab import build_help_tab


def build_ui(app: 'App') -> None:
    """Build the main UI using CustomTkinter with professional layout."""
    # Build toolbar
    build_toolbar(app)
    
    # Main container with padding
    main_container = ctk.CTkFrame(app, fg_color="transparent")
    main_container.pack(fill="both", expand=True, padx=12, pady=(12, 0))
    
    # Use CTkTabview for professional tabbed interface
    main_tabs = ctk.CTkTabview(main_container)
    main_tabs.pack(fill="both", expand=True, pady=(0, 12))
    
    # Tab 1: Editor (File Explorer + Preview + Search & Edits)
    editor_tab = main_tabs.add("Editor")
    build_editor_tab(app, editor_tab)
    
    # Tab 2: General Settings
    general_tab = main_tabs.add("General Settings")
    build_general_settings_tab(app, general_tab)
    
    # Tab 3: Multi-Packer
    packer_tab = main_tabs.add("Multi-Packer")
    build_multi_packer_tab(app, packer_tab)
    
    # Tab 4: Colors
    colors_tab = main_tabs.add("Colors")
    build_colors_tab(app, colors_tab)
    
    # Tab 5: Help
    help_tab = main_tabs.add("Help")
    build_help_tab(app, help_tab)
    
    # Store tabview reference for switching tabs
    app.main_tabs = main_tabs
    
    # Status bar at the bottom
    status_bar = ctk.CTkFrame(app, height=32, fg_color=("gray85", "gray18"), border_width=1, border_color=("gray70", "gray30"))
    status_bar.pack(side="bottom", fill="x", padx=0, pady=0)
    status_bar.pack_propagate(False)
    
    status_container = ctk.CTkFrame(status_bar, fg_color="transparent")
    status_container.pack(fill="both", expand=True, padx=12, pady=6)
    
    # Status dot (colored indicator)
    app.status_dot = ctk.CTkLabel(
        status_container,
        text="●",
        font=ctk.CTkFont(size=14),
        width=16,
        height=16
    )
    app.status_dot.pack(side="left", padx=(0, 8))
    app.status_dot.configure(text_color="#4CAF50")  # Green for ready
    
    # Status text
    app.status = ctk.StringVar(value="Ready")
    status_label = ctk.CTkLabel(
        status_container,
        textvariable=app.status,
        font=ctk.CTkFont(size=11),
        anchor="w"
    )
    status_label.pack(side="left")
    
    # Helper function to update status with color
    def update_status(message: str, color: str = "#4CAF50"):
        """Update status message with colored dot."""
        app.status.set(message)
        app.status_dot.configure(text_color=color)
    
    # Store the update function in app for easy access
    app._update_status = update_status
