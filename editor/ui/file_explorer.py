"""File explorer panel for the editor tab."""

import customtkinter as ctk
from tkinter import ttk
from typing import TYPE_CHECKING

from ui.utils import is_dark_mode

if TYPE_CHECKING:
    from core.app import App


def build_file_explorer(app: "App", parent) -> None:
    """Build the file explorer panel."""
    # Enhanced header with better styling
    explorer_header = ctk.CTkFrame(parent, fg_color="transparent")
    explorer_header.pack(fill="x", padx=12, pady=(10, 8))

    explorer_title = ctk.CTkLabel(
        explorer_header,
        text="Project Files",
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color=("gray10", "gray90"),
    )
    explorer_title.pack(side="left")
    
    # File hover status indicator (right side of header)
    file_status_frame = ctk.CTkFrame(explorer_header, fg_color="transparent")
    file_status_frame.pack(side="right", fill="x", expand=True, padx=(8, 0))
    
    # File hover status text
    app.file_hover_status = ctk.StringVar(value="")
    file_status_label = ctk.CTkLabel(
        file_status_frame,
        textvariable=app.file_hover_status,
        font=ctk.CTkFont(size=10),
        text_color=("gray50", "gray70"),
        anchor="e"
    )
    file_status_label.pack(side="right")

    # Enhanced search entry styling
    app.file_search_var = ctk.StringVar(value="")
    app.file_search_entry = ctk.CTkEntry(
        parent,
        textvariable=app.file_search_var,
        height=32,
        font=ctk.CTkFont(size=11),
        corner_radius=6,
        border_width=1,
        border_color=("gray75", "gray30"),
    )
    app.file_search_entry.pack(fill="x", padx=12, pady=(0, 10))
    app.file_search_var.trace_add("write", lambda *args: app._on_file_search_change(*args))

    # Enhanced tree frame with better styling
    tree_frame = ctk.CTkFrame(
        parent,
        fg_color=("gray98", "gray18"),
        corner_radius=8,
        border_width=1,
        border_color=("gray80", "gray25"),
    )
    tree_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))

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
    app.tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)

    scrollbar = ctk.CTkScrollbar(
        tree_frame,
        command=app.tree.yview,
        orientation="vertical",
    )
    scrollbar.pack(side="right", fill="y", padx=0, pady=0)
    app.tree.configure(yscrollcommand=scrollbar.set)
    app.tree.bind("<<TreeviewSelect>>", app._on_tree_select)

    def on_tree_hover(event):
        """Show tooltip with full relative path on hover in file explorer header."""
        item = app.tree.identify_row(event.y)
        if item:
            tooltip_text = app.tree.set(item, "tooltip")
            if tooltip_text:
                # Update hover status in file explorer header
                if hasattr(app, 'file_hover_status'):
                    app.file_hover_status.set(tooltip_text)
                elif hasattr(app, '_update_hover_status'):
                    app._update_hover_status(tooltip_text)

    def on_tree_leave(_event):
        """Clear tooltip on leave."""
        # Clear hover status in file explorer header
        if hasattr(app, 'file_hover_status'):
            app.file_hover_status.set("")
        elif hasattr(app, '_update_hover_status'):
            app._update_hover_status("")

    app.tree.bind("<Motion>", on_tree_hover)
    app.tree.bind("<Leave>", on_tree_leave)

