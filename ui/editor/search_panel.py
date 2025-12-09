"""Search panel for parameters and results list."""

import customtkinter as ctk
import tkinter as tk
from typing import TYPE_CHECKING

from ..utils import get_listbox_colors

if TYPE_CHECKING:
    from core.app import App


def build_search_panel(app: "App", parent) -> None:
    """Build the search panel."""
    search_panel = parent

    search_header = ctk.CTkFrame(search_panel, fg_color="transparent")
    search_header.pack(fill="x", padx=10, pady=(8, 6))

    search_title = ctk.CTkLabel(
        search_header,
        text="Parameter Search",
        font=ctk.CTkFont(size=13, weight="bold"),
    )
    search_title.pack(side="left")

    search_input_frame = ctk.CTkFrame(search_panel, fg_color="transparent")
    search_input_frame.pack(fill="x", padx=10, pady=(0, 6))

    app.search_var = ctk.StringVar()
    app.ent_search = ctk.CTkEntry(
        search_input_frame,
        textvariable=app.search_var,
        placeholder_text="Enter search criteria...",
        height=30,
        font=ctk.CTkFont(size=11),
        corner_radius=6,
    )
    app.ent_search.pack(side="left", fill="x", expand=True, padx=(0, 6))
    app.ent_search.bind("<Return>", lambda event: app._find_params())

    app.find_btn = ctk.CTkButton(
        search_input_frame,
        text="Find",
        command=app._find_params,
        width=80,
        height=30,
        font=ctk.CTkFont(size=11),
        corner_radius=6,
    )
    app.find_btn.pack(side="left")

    hint_frame = ctk.CTkFrame(
        search_panel,
        fg_color=("gray95", "gray20"),
        corner_radius=4,
        border_width=1,
        border_color=("gray85", "gray30"),
    )
    hint_frame.pack(fill="x", padx=10, pady=(0, 6))

    results_hint = ctk.CTkLabel(
        hint_frame,
        text="💡 Single-click to preview • Double-click to add modification",
        font=ctk.CTkFont(size=11),
        text_color=("gray30", "gray80"),
        anchor="w",
        justify="left",
    )
    results_hint.pack(fill="x", padx=8, pady=6)

    results_container = ctk.CTkFrame(search_panel, fg_color="transparent")
    results_container.pack(fill="both", expand=True, padx=10, pady=(0, 8))

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
    app.lst_results.pack(side="left", fill="both", expand=True)

    results_scrollbar = ctk.CTkScrollbar(results_container, command=app.lst_results.yview, orientation="vertical")
    results_scrollbar.pack(side="right", fill="y")
    app.lst_results.configure(yscrollcommand=results_scrollbar.set)
    app.lst_results.bind("<Double-Button-1>", app._on_add_from_result)
    app.lst_results.bind("<ButtonRelease-1>", app._on_result_select)

