"""Preview panel for file display and syntax highlighting."""

import customtkinter as ctk
import tkinter as tk
from typing import TYPE_CHECKING

from ..utils import get_preview_colors

if TYPE_CHECKING:
    from core.app import App


def build_preview_panel(app: "App", parent) -> None:
    """Build the preview panel."""
    preview_header = ctk.CTkFrame(parent, fg_color="transparent")
    preview_header.pack(fill="x", padx=10, pady=(8, 6))

    app.preview_label = ctk.CTkLabel(
        preview_header,
        text="File Preview: —",
        font=ctk.CTkFont(size=13, weight="bold"),
    )
    app.preview_label.pack(side="left")
    
    # Export as TXT button
    export_btn = ctk.CTkButton(
        preview_header,
        text="Export as TXT",
        width=100,
        height=28,
        font=ctk.CTkFont(size=11),
        command=app._export_file_as_txt,
        corner_radius=4
    )
    export_btn.pack(side="right")

    preview_container = ctk.CTkFrame(parent, fg_color="transparent")
    preview_container.pack(fill="both", expand=True, padx=10, pady=(0, 8))

    bg_color, fg_color, highlight_bg = get_preview_colors()

    text_frame = tk.Frame(preview_container, bg=bg_color)
    text_frame.pack(side="left", fill="both", expand=True)

    line_number_width = 4
    app.line_numbers = tk.Text(
        text_frame,
        width=line_number_width,
        padx=4,
        pady=12,
        takefocus=0,
        wrap="none",
        state="disabled",
        font=("Consolas", 11),
        bg=bg_color,
        fg=fg_color,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        insertbackground=fg_color,
    )
    app.line_numbers.pack(side="left", fill="y")

    app.txt = tk.Text(
        text_frame,
        wrap="none",
        font=("Consolas", 11),
        state="disabled",
        bg=bg_color,
        fg=fg_color,
        insertbackground=fg_color,
        borderwidth=0,
        highlightthickness=0,
        padx=12,
        pady=12,
        exportselection=False,
        selectbackground=bg_color,
        selectforeground=fg_color,
    )
    app.txt.pack(side="left", fill="both", expand=True)

    # Dark theme highlight colors - distinct from each other
    hover_bg = "#2d2d30"  # Gray - for mouse hover over a line
    edited_line_bg = "#2a3a3a"  # Dark teal/green - for lines that have edits (persistent)
    
    app.txt.tag_configure("hover", background=hover_bg)
    app.txt.tag_configure("highlight", background=highlight_bg)  # Dark yellow/green - when you click an edit in the list
    app.txt.tag_configure("edited_line", background=edited_line_bg)

    def on_mouse_motion(event):
        try:
            index = app.txt.index(f"@{event.x},{event.y}")
            line_num = index.split(".")[0]
            app.txt.tag_remove("hover", "1.0", "end")
            line_start = f"{line_num}.0"
            line_end = f"{line_num}.end"
            line_content = app.txt.get(line_start, line_end).strip()
            if line_content:
                app.txt.tag_add("hover", line_start, line_end)
        except Exception:
            pass

    def on_mouse_leave(_event):
        app.txt.tag_remove("hover", "1.0", "end")

    app.txt.bind("<Motion>", on_mouse_motion)
    app.txt.bind("<Leave>", on_mouse_leave)

    def prevent_selection(_event):
        return "break"

    # Don't prevent Button-1 to allow double-click to work
    # Selection is already disabled via exportselection=False
    app.txt.bind("<B1-Motion>", prevent_selection)
    app.txt.bind("<ButtonRelease-1>", prevent_selection)
    app.txt.bind("<Shift-Button-1>", prevent_selection)
    app.txt.bind("<Control-Button-1>", prevent_selection)

    def update_line_numbers():
        try:
            content = app.txt.get("1.0", "end-1c")
            line_count = len(content.splitlines())
            if content and not content.endswith("\n"):
                line_count += 1

            app.line_numbers.config(state="normal")
            app.line_numbers.delete("1.0", "end")
            # Only show line numbers if there's content
            if line_count > 0:
                for i in range(1, line_count + 1):
                    app.line_numbers.insert("end", f"{i}\n")
            app.line_numbers.config(state="disabled")

            try:
                top = app.txt.yview()[0]
                app.line_numbers.yview_moveto(top)
            except Exception:
                pass
        except Exception:
            pass

    app._update_line_numbers = update_line_numbers

    def sync_scroll():
        try:
            top = app.txt.yview()[0]
            app.line_numbers.yview_moveto(top)
        except Exception:
            pass

    preview_scrollbar = ctk.CTkScrollbar(preview_container, orientation="vertical")
    preview_scrollbar.pack(side="right", fill="y")

    def scrollbar_command(*args):
        app.txt.yview(*args)
        sync_scroll()

    def text_scroll_command(*args):
        sync_scroll()
        preview_scrollbar.set(*args)

    preview_scrollbar.configure(command=scrollbar_command)
    app.txt.configure(yscrollcommand=text_scroll_command)

    app.txt.bind("<Double-Button-1>", app._on_preview_double_click)
    app.txt.bind("<Button-3>", app._on_preview_right_click)

