"""Search panel for parameters and results list."""

import customtkinter as ctk
import tkinter as tk
from typing import TYPE_CHECKING

from ui.utils import get_listbox_colors

if TYPE_CHECKING:
    from core.app import App


def build_search_panel(app: "App", parent) -> None:
    """Build the search panel."""
    search_panel = parent

    # Enhanced header with better styling
    search_header = ctk.CTkFrame(search_panel, fg_color="transparent")
    search_header.pack(fill="x", padx=12, pady=(10, 8))

    search_title = ctk.CTkLabel(
        search_header,
        text="Code Search",
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color=("gray10", "gray90"),
    )
    search_title.pack(side="left")
    
    # Search status indicator (right side of header)
    search_status_frame = ctk.CTkFrame(search_header, fg_color="transparent")
    search_status_frame.pack(side="right", padx=(8, 0))
    
    # Search status text
    app.search_status = ctk.StringVar(value="")
    search_status_label = ctk.CTkLabel(
        search_status_frame,
        textvariable=app.search_status,
        font=ctk.CTkFont(size=10),
        text_color=("gray50", "gray70"),
        anchor="e"
    )
    search_status_label.pack(side="left")

    # Enhanced input frame styling
    search_input_frame = ctk.CTkFrame(search_panel, fg_color="transparent")
    search_input_frame.pack(fill="x", padx=12, pady=(0, 8))

    app.search_var = ctk.StringVar(value="")
    app.ent_search = ctk.CTkEntry(
        search_input_frame,
        textvariable=app.search_var,
        height=32,
        font=ctk.CTkFont(size=11),
        corner_radius=6,
        border_width=1,
        border_color=("gray75", "gray30"),
    )
    app.ent_search.pack(side="left", fill="x", expand=True, padx=(0, 8))
    app.ent_search.bind("<Return>", lambda event: app._find_params())

    # Enhanced button styling
    app.find_btn = ctk.CTkButton(
        search_input_frame,
        text="Find",
        command=app._find_params,
        width=90,
        height=32,
        font=ctk.CTkFont(size=11, weight="normal"),
        corner_radius=6,
        fg_color=("gray85", "gray25"),
        hover_color=("gray75", "gray35"),
        border_width=1,
        border_color=("gray75", "gray30"),
    )
    app.find_btn.pack(side="left")

    # Enhanced hint frame styling
    hint_frame = ctk.CTkFrame(
        search_panel,
        fg_color=("gray95", "gray20"),
        corner_radius=6,
        border_width=1,
        border_color=("gray85", "gray30"),
    )
    hint_frame.pack(fill="x", padx=12, pady=(0, 8))

    results_hint = ctk.CTkLabel(
        hint_frame,
        text="💡 Single-click to preview • Double-click to add modification",
        font=ctk.CTkFont(size=11),
        text_color=("gray30", "gray80"),
        anchor="w",
        justify="left",
    )
    results_hint.pack(fill="x", padx=10, pady=8)

    # Enhanced results container styling
    results_container = ctk.CTkFrame(
        search_panel,
        fg_color=("gray98", "gray18"),
        corner_radius=8,
        border_width=1,
        border_color=("gray80", "gray25"),
    )
    results_container.pack(fill="both", expand=True, padx=12, pady=(0, 10))

    listbox_bg, listbox_fg, listbox_selectbg = get_listbox_colors()

    app.lst_results = tk.Listbox(
        results_container,
        font=("Segoe UI", 10),
        bg=listbox_bg,
        fg=listbox_fg,
        selectbackground=listbox_selectbg,
        selectforeground="white",
        borderwidth=0,
        highlightthickness=0,
        activestyle="none",
    )
    app.lst_results.pack(side="left", fill="both", expand=True, padx=2, pady=2)

    results_scrollbar = ctk.CTkScrollbar(
        results_container,
        command=app.lst_results.yview,
        orientation="vertical",
    )
    results_scrollbar.pack(side="right", fill="y", padx=0, pady=0)
    app.lst_results.configure(yscrollcommand=results_scrollbar.set)
    app.lst_results.bind("<Double-Button-1>", app._on_add_from_result)
    app.lst_results.bind("<ButtonRelease-1>", app._on_result_select)

