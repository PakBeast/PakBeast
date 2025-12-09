"""File explorer panel for the editor tab."""

import customtkinter as ctk
from tkinter import ttk
from typing import TYPE_CHECKING

from ..utils import is_dark_mode

if TYPE_CHECKING:
    from core.app import App


def build_file_explorer(app: "App", parent) -> None:
    """Build the file explorer panel."""
    explorer_header = ctk.CTkFrame(parent, fg_color="transparent")
    explorer_header.pack(fill="x", padx=10, pady=(8, 6))

    explorer_title = ctk.CTkLabel(
        explorer_header,
        text="Project Files",
        font=ctk.CTkFont(size=13, weight="bold"),
    )
    explorer_title.pack(side="left")

    app.file_search_var = ctk.StringVar()
    app.file_search_entry = ctk.CTkEntry(
        parent,
        textvariable=app.file_search_var,
        placeholder_text="Search files by name...",
        height=30,
        font=ctk.CTkFont(size=11),
        corner_radius=6,
    )
    app.file_search_entry.pack(fill="x", padx=10, pady=(0, 8))
    app.file_search_var.trace_add("write", lambda *args: app._on_file_search_change(*args))

    tree_frame = ctk.CTkFrame(parent, fg_color="transparent")
    tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 8))

    style = ttk.Style()
    dark = is_dark_mode()
    style.theme_use("clam")
    if dark:
        style.configure(
            "Treeview",
            background="#212121",
            foreground="#FFFFFF",
            fieldbackground="#212121",
            borderwidth=0,
        )
        style.map("Treeview", background=[("selected", "#1f538d")])
    else:
        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground="#000000",
            fieldbackground="#FFFFFF",
            borderwidth=0,
        )
        style.map("Treeview", background=[("selected", "#0078d4")])

    app.tree = ttk.Treeview(
        tree_frame,
        columns=("abspath", "tooltip"),
        show="tree",
        selectmode="browse",
    )
    app.tree.column("#0", width=200, minwidth=100)
    app.tree.column("abspath", width=0, stretch=False)
    app.tree.column("tooltip", width=0, stretch=False)
    app.tree.pack(side="left", fill="both", expand=True)

    scrollbar = ctk.CTkScrollbar(tree_frame, command=app.tree.yview, orientation="vertical")
    scrollbar.pack(side="right", fill="y")
    app.tree.configure(yscrollcommand=scrollbar.set)
    app.tree.bind("<<TreeviewSelect>>", app._on_tree_select)

    def on_tree_hover(event):
        """Show tooltip with full relative path on hover."""
        item = app.tree.identify_row(event.y)
        if item:
            tooltip_text = app.tree.set(item, "tooltip")
            if tooltip_text:
                app.status.set(f"Path: {tooltip_text}")

    def on_tree_leave(_event):
        """Clear tooltip on leave."""
        app.status.set("Ready")

    app.tree.bind("<Motion>", on_tree_hover)
    app.tree.bind("<Leave>", on_tree_leave)

