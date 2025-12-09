"""Active edits panel with search, filters, and list."""

import customtkinter as ctk
import tkinter as tk
from typing import TYPE_CHECKING

from ..utils import get_listbox_colors
from .config import EDIT_TYPE_FILTER_LAYOUT

if TYPE_CHECKING:
    from core.app import App


def build_edits_panel(app: "App", parent) -> None:
    """Build the active edits panel."""
    edits_panel = parent

    edits_header = ctk.CTkFrame(edits_panel, fg_color="transparent")
    edits_header.pack(fill="x", padx=10, pady=(8, 6))

    edits_title = ctk.CTkLabel(
        edits_header,
        text="Active Modifications",
        font=ctk.CTkFont(size=13, weight="bold"),
    )
    edits_title.pack(side="left")

    search_actions_frame = ctk.CTkFrame(edits_panel, fg_color="transparent")
    search_actions_frame.pack(fill="x", padx=10, pady=(0, 6))

    app.search_edits_var = ctk.StringVar()
    app.search_edits_entry = ctk.CTkEntry(
        search_actions_frame,
        textvariable=app.search_edits_var,
        placeholder_text="Filter modifications...",
        height=30,
        font=ctk.CTkFont(size=11),
    )
    app.search_edits_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
    app.search_edits_var.trace_add("write", lambda *args: app._on_filter_change_debounced(*args))

    bulk_actions = ["Enable All Filtered", "Disable All Filtered", "Clear All Modifications"]
    app.bulk_action_var = ctk.StringVar(value=bulk_actions[0])

    def handle_bulk_action(choice: str):
        if choice == "Enable All Filtered":
            app._enable_all_filtered()
        elif choice == "Disable All Filtered":
            app._disable_all_filtered()
        elif choice == "Clear All Modifications":
            app._clear_edits()
        app.bulk_action_var.set(bulk_actions[0])

    bulk_action_menu = ctk.CTkOptionMenu(
        search_actions_frame,
        variable=app.bulk_action_var,
        values=bulk_actions,
        width=170,
        height=30,
        command=handle_bulk_action,
        font=ctk.CTkFont(size=11),
    )
    bulk_action_menu.pack(side="left", padx=(6, 0))

    filter_row = ctk.CTkFrame(edits_panel, fg_color="transparent")
    filter_row.pack(fill="x", padx=10, pady=(0, 6))

    edit_types = ["All Edit Types", "VALUE_REPLACE", "BLOCK_DELETE", "LINE_DELETE", "LINE_REPLACE", "LINE_INSERT"]
    app.filter_edit_type = ctk.StringVar(value=edit_types[0])

    def on_edit_type_change(value: str):
        app.filter_edit_type.set(value)
        app._on_filter_change()

    if EDIT_TYPE_FILTER_LAYOUT == "segmented":
        app.type_filter_segmented = ctk.CTkSegmentedButton(
            filter_row,
            values=edit_types,
            variable=app.filter_edit_type,
            height=30,
            font=ctk.CTkFont(size=11),
            corner_radius=6,
            command=on_edit_type_change,
        )
        app.type_filter_segmented.pack(side="left", padx=(0, 6))
    else:
        app.type_filter_combo = ctk.CTkComboBox(
            filter_row,
            values=edit_types,
            variable=app.filter_edit_type,
            width=160,
            height=30,
            font=ctk.CTkFont(size=11),
            corner_radius=6,
            dropdown_font=ctk.CTkFont(size=11),
            state="readonly",
        )
        app.type_filter_combo.pack(side="left", padx=(0, 6))
        app.type_filter_combo.configure(command=on_edit_type_change)

    app.filter_file_path = ctk.StringVar(value="All Files")
    app.file_filter_combo = ctk.CTkComboBox(
        filter_row,
        values=["All Files"],
        variable=app.filter_file_path,
        width=160,
        height=30,
        font=ctk.CTkFont(size=11),
        corner_radius=6,
        dropdown_font=ctk.CTkFont(size=11),
        state="readonly",
    )
    app.file_filter_combo.pack(side="left")
    app.file_filter_combo.configure(command=lambda v: app._on_filter_change())

    edits_container = ctk.CTkFrame(edits_panel, fg_color="transparent")
    edits_container.pack(fill="both", expand=True, padx=10, pady=(0, 8))

    listbox_bg, listbox_fg, listbox_selectbg = get_listbox_colors()

    app.lst_edits = tk.Listbox(
        edits_container,
        font=("Segoe UI", 10),
        bg=listbox_bg,
        fg=listbox_fg,
        selectbackground=listbox_selectbg,
        selectforeground="white",
        borderwidth=0,
        highlightthickness=0,
        activestyle="none",
    )
    app.lst_edits.pack(side="left", fill="both", expand=True)

    edits_scrollbar = ctk.CTkScrollbar(edits_container, command=app.lst_edits.yview, orientation="vertical")
    edits_scrollbar.pack(side="right", fill="y")
    app.lst_edits.configure(yscrollcommand=edits_scrollbar.set)
    app.lst_edits.bind("<Button-3>", app._edits_context)
    app.lst_edits.bind("<Double-Button-1>", lambda _e: app._toggle_selected_edit())
    app.lst_edits.bind("<ButtonRelease-1>", app._on_edit_select)

