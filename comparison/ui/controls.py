"""Comparison tab controls (file selectors, context, compare button)."""

from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from core.app import App


def _set_status(app: "App", message: str, color: str = "#4CAF50") -> None:
    if hasattr(app, "_update_status"):
        app._update_status(message, color)
    else:
        app.status.set(message)


def build_controls(app: "App", parent: ctk.CTkFrame) -> Dict:
    """Build the controls section (file selectors, context, compare button)."""
    controls = ctk.CTkFrame(parent, fg_color="transparent")
    controls.pack(fill="x", pady=(0, 12))

    # Original file selector (single file only)
    original_label = ctk.CTkLabel(
        controls,
        text="Original TXT File:",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=("gray10", "gray90"),
    )
    original_label.pack(side="left", padx=(0, 8))

    original_var = ctk.StringVar(value="")
    original_entry = ctk.CTkEntry(
        controls,
        textvariable=original_var,
        width=400,
        height=32,
        font=ctk.CTkFont(size=11),
        corner_radius=6,
        border_width=1,
        border_color=("gray75", "gray30"),
        placeholder_text="Select original TXT file...",
    )
    original_entry.pack(side="left", padx=(0, 8))

    def pick_original():
        file = filedialog.askopenfilename(
            title="Select Original TXT File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=app.settings.last_export_dir if hasattr(app.settings, 'last_export_dir') and app.settings.last_export_dir else None,
        )
        if file:
            original_var.set(file)
            _set_status(app, f"Original file selected: {Path(file).name}")

    pick_original_btn = ctk.CTkButton(
        controls,
        text="Select Original",
        command=pick_original,
        width=120,
        height=32,
        font=ctk.CTkFont(size=11, weight="normal"),
        corner_radius=6,
        fg_color=("gray85", "gray25"),
        hover_color=("gray75", "gray35"),
        border_width=1,
        border_color=("gray75", "gray30"),
    )
    pick_original_btn.pack(side="left", padx=(0, 12))

    # Modded file selector (single file only)
    modded_label = ctk.CTkLabel(
        controls,
        text="Modded TXT File:",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=("gray10", "gray90"),
    )
    modded_label.pack(side="left", padx=(0, 8))

    modded_var = ctk.StringVar(value="")
    modded_entry = ctk.CTkEntry(
        controls,
        textvariable=modded_var,
        width=400,
        height=32,
        font=ctk.CTkFont(size=11),
        corner_radius=6,
        border_width=1,
        border_color=("gray75", "gray30"),
        placeholder_text="Select modded TXT file...",
    )
    modded_entry.pack(side="left", padx=(0, 8))

    def pick_modded():
        file = filedialog.askopenfilename(
            title="Select Modded TXT File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=app.settings.last_export_dir if hasattr(app.settings, 'last_export_dir') and app.settings.last_export_dir else None,
        )
        if file:
            modded_var.set(file)
            _set_status(app, f"Modded file selected: {Path(file).name}")

    pick_modded_btn = ctk.CTkButton(
        controls,
        text="Select Modded",
        command=pick_modded,
        width=120,
        height=32,
        font=ctk.CTkFont(size=11, weight="normal"),
        corner_radius=6,
        fg_color=("gray85", "gray25"),
        hover_color=("gray75", "gray35"),
        border_width=1,
        border_color=("gray75", "gray30"),
    )
    pick_modded_btn.pack(side="left", padx=(0, 12))

    # Context lines
    ctx_label = ctk.CTkLabel(
        controls,
        text="Context:",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=("gray10", "gray90"),
    )
    ctx_label.pack(side="left", padx=(0, 6))
    ctx_var = ctk.StringVar(value="3")
    ctx_entry = ctk.CTkEntry(
        controls,
        textvariable=ctx_var,
        width=50,
        height=32,
        font=ctk.CTkFont(size=11),
        corner_radius=6,
        border_width=1,
        border_color=("gray75", "gray30"),
    )
    ctx_entry.pack(side="left", padx=(0, 12))

    # Compare button - enhanced styling
    compare_btn = ctk.CTkButton(
        controls,
        text="Compare",
        width=100,
        height=32,
        font=ctk.CTkFont(size=11, weight="normal"),
        corner_radius=6,
        fg_color=("gray85", "gray25"),
        hover_color=("gray75", "gray35"),
        border_width=1,
        border_color=("gray75", "gray30"),
    )
    compare_btn.pack(side="left")
    
    return {
        "original_var": original_var,
        "modded_var": modded_var,
        "ctx_var": ctx_var,
        "compare_btn": compare_btn,
    }
