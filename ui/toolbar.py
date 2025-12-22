"""Toolbar building functions."""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App


def build_toolbar(app: 'App') -> None:
    """Build the toolbar with quick access buttons."""
    toolbar = ctk.CTkFrame(app, height=48, fg_color="transparent", border_width=0)
    toolbar.pack(side="top", fill="x", padx=0, pady=0)
    toolbar.pack_propagate(False)
    
    # Main toolbar container
    toolbar_container = ctk.CTkFrame(toolbar, fg_color="transparent")
    toolbar_container.pack(fill="both", expand=True, padx=16, pady=8)
    
    # Centered button container
    button_container = ctk.CTkFrame(toolbar_container, fg_color="transparent")
    button_container.pack(expand=True)
    
    # Open Game Data button
    load_btn = ctk.CTkButton(
        button_container,
        text="Open Game Data",
        width=115,
        height=32,
        font=ctk.CTkFont(size=11, weight="normal"),
        command=app._load_pak,
        corner_radius=6,
        fg_color=("gray85", "gray25"),
        hover_color=("gray75", "gray35"),
        border_width=1,
        border_color=("gray75", "gray30"),
    )
    load_btn.pack(side="left", padx=(0, 8))
    
    # Save Project button
    save_btn = ctk.CTkButton(
        button_container,
        text="Save Project",
        width=105,
        height=32,
        font=ctk.CTkFont(size=11, weight="normal"),
        command=app._save_project,
        corner_radius=6,
        fg_color=("gray85", "gray25"),
        hover_color=("gray75", "gray35"),
        border_width=1,
        border_color=("gray75", "gray30"),
    )
    save_btn.pack(side="left", padx=(0, 8))
    
    # Load Project button
    load_proj_btn = ctk.CTkButton(
        button_container,
        text="Load Project",
        width=105,
        height=32,
        font=ctk.CTkFont(size=11, weight="normal"),
        command=app._load_project,
        corner_radius=6,
        fg_color=("gray85", "gray25"),
        hover_color=("gray75", "gray35"),
        border_width=1,
        border_color=("gray75", "gray30"),
    )
    load_proj_btn.pack(side="left", padx=(0, 8))
    
    # Build Mod button
    pack_btn = ctk.CTkButton(
        button_container,
        text="Build Mod",
        width=100,
        height=32,
        font=ctk.CTkFont(size=11, weight="normal"),
        command=app._pack_pak,
        corner_radius=6,
        fg_color=("gray85", "gray25"),
        hover_color=("gray75", "gray35"),
        border_width=1,
        border_color=("gray75", "gray30"),
    )
    pack_btn.pack(side="left")

