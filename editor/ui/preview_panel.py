"""Preview panel for file display and syntax highlighting."""

import customtkinter as ctk
import tkinter as tk
from typing import TYPE_CHECKING

from ui.utils import get_preview_colors

if TYPE_CHECKING:
    from core.app import App


def build_preview_panel(app: "App", parent) -> None:
    """Build the preview panel."""
    # Enhanced header with better styling
    preview_header = ctk.CTkFrame(parent, fg_color="transparent")
    preview_header.pack(fill="x", padx=14, pady=(12, 8))

    app.preview_label = ctk.CTkLabel(
        preview_header,
        text="File Preview:"
        ,
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color=("gray10", "gray90"),
    )
    app.preview_label.pack(side="left")
    
    # Search and Export controls frame (new line under File Preview) - enhanced styling
    search_controls_frame = ctk.CTkFrame(parent, fg_color="transparent")
    search_controls_frame.pack(fill="x", padx=14, pady=(0, 8))
    
    # Enhanced preview container with better styling
    preview_container = ctk.CTkFrame(
        parent,
        fg_color=("gray98", "gray18"),
        corner_radius=8,
        border_width=1,
        border_color=("gray80", "gray25"),
    )
    preview_container.pack(fill="both", expand=True, padx=14, pady=(0, 12))

    bg_color, fg_color, highlight_bg = get_preview_colors()

    text_frame = tk.Frame(preview_container, bg=bg_color)
    text_frame.pack(side="left", fill="both", expand=True)

    # Start with a default width, will be adjusted dynamically
    app.line_numbers = tk.Text(
        text_frame,
        width=4,
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
                # Calculate width needed for line numbers (add 1 for padding)
                # Use number of digits in the largest line number
                max_line_digits = len(str(line_count))
                # Set width to accommodate the largest line number + 1 for spacing
                # Minimum width of 4, maximum reasonable width of 12
                line_number_width = max(4, min(max_line_digits + 1, 12))
                app.line_numbers.config(width=line_number_width)
                
                # Format line numbers with right alignment by padding
                for i in range(1, line_count + 1):
                    # Right-align by padding with spaces
                    line_num_str = f"{i:>{max_line_digits}}\n"
                    app.line_numbers.insert("end", line_num_str)
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

    preview_scrollbar = ctk.CTkScrollbar(
        preview_container,
        orientation="vertical",
    )
    preview_scrollbar.pack(side="right", fill="y", padx=0, pady=0)

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
    
    # Setup search functionality in search_controls_frame (new line under File Preview)
    _setup_search_functionality(app, search_controls_frame)


def _setup_search_functionality(app: "App", parent):
    """Set up search functionality for the preview panel (always visible)."""
    
    # Store search state
    app._search_matches = []
    app._current_match_index = -1
    app._search_tag_name = "search_match"
    app._search_current_tag_name = "search_current"
    
    # Configure search highlight tags
    app.txt.tag_configure(app._search_tag_name, background="#FFD700", foreground="#000000")  # Yellow highlight
    app.txt.tag_configure(app._search_current_tag_name, background="#FF6B00", foreground="#FFFFFF")  # Orange for current match
    
    # Search entry and controls (horizontal layout, aligned left with File Preview)
    # Order from left to right: search_entry, export_btn, match_count_label
    search_var = ctk.StringVar(value="")
    
    # Search entry (leftmost, aligned with File Preview)
    search_entry = ctk.CTkEntry(
        parent,
        textvariable=search_var,
        width=260,
        font=ctk.CTkFont(size=11),
        height=32,
        corner_radius=6,
        border_width=1,
        border_color=("gray75", "gray30"),
    )
    search_entry.pack(side="left", padx=(0, 8))
    
    # Export button (to the right of search box) - enhanced styling
    export_btn = ctk.CTkButton(
        parent,
        text="Export",
        width=100,
        height=32,
        font=ctk.CTkFont(size=11, weight="normal"),
        command=app._export_file_as_txt,
        corner_radius=6,
        fg_color=("gray85", "gray25"),
        hover_color=("gray75", "gray35"),
        border_width=1,
        border_color=("gray75", "gray30"),
    )
    export_btn.pack(side="left", padx=(0, 8))
    
    # Match count label (to the right of export button) - enhanced styling
    match_count_label = ctk.CTkLabel(
        parent,
        text="",
        font=ctk.CTkFont(size=10),
        text_color=("gray50", "gray70"),
        width=70,
    )
    match_count_label.pack(side="left", padx=(0, 0))
    
    
    def perform_search(*args):
        """Perform search and highlight matches."""
        search_text = search_var.get()
        
        # Clear previous highlights
        app.txt.tag_remove(app._search_tag_name, "1.0", "end")
        app.txt.tag_remove(app._search_current_tag_name, "1.0", "end")
        app._search_matches = []
        app._current_match_index = -1
        
        if not search_text:
            match_count_label.configure(text="")
            return
        
        # Use tkinter's built-in search method with case-insensitive option
        start_pos = "1.0"
        matches = []
        
        # Search is case-insensitive - "dropped" will find "Dropped", "DROPPED", etc.
        while True:
            # Search for the text (plain text search, case-insensitive)
            pos = app.txt.search(search_text, start_pos, "end", nocase=True)
            if not pos:
                break
            
            # Calculate end position
            end_pos = app.txt.index(f"{pos}+{len(search_text)}c")
            
            # Add highlight
            app.txt.tag_add(app._search_tag_name, pos, end_pos)
            matches.append((pos, end_pos))
            
            # Move start position for next search
            start_pos = end_pos
        
        app._search_matches = matches
        
        # Update match count
        match_count = len(app._search_matches)
        if match_count == 0:
            match_count_label.configure(text="No matches")
        else:
            # Show as "current/total" format
            app._current_match_index = 0
            match_count_label.configure(text=f"1/{match_count}")
            _navigate_match(app, 0)
    
    def _navigate_match(app: "App", direction: int):
        """Navigate to next/previous match."""
        if not app._search_matches:
            match_count_label.configure(text="No matches")
            return
        
        # Remove current match highlight
        app.txt.tag_remove(app._search_current_tag_name, "1.0", "end")
        
        # Update index
        if direction == 0:
            # Just highlight current without moving
            app._current_match_index = 0
        else:
            # Navigate: 1 for next, -1 for previous
            app._current_match_index = (app._current_match_index + direction) % len(app._search_matches)
        
        # Highlight current match
        if 0 <= app._current_match_index < len(app._search_matches):
            start_index, end_index = app._search_matches[app._current_match_index]
            app.txt.tag_add(app._search_current_tag_name, start_index, end_index)
            
            # Scroll to make it visible
            app.txt.see(start_index)
            
            # Update match count to show current position as "current/total"
            match_count = len(app._search_matches)
            current = app._current_match_index + 1
            match_count_label.configure(text=f"{current}/{match_count}")
    
    # Bind search entry changes
    search_var.trace_add("write", perform_search)
    
    # Bind Enter key to navigate to next match
    search_entry.bind("<Return>", lambda e: _navigate_match(app, 1))
    search_entry.bind("<Shift-Return>", lambda e: _navigate_match(app, -1))
    
    # Optional: Bind Ctrl+F to focus search entry (but panel is always visible)
    def focus_search(event):
        search_entry.focus_set()
        search_entry.select_range(0, tk.END)
        return "break"
    
    # Bind to the main window and text widget
    app.bind_all("<Control-f>", focus_search)
    app.bind_all("<Control-F>", focus_search)
    app.txt.bind("<Control-f>", focus_search)
    app.txt.bind("<Control-F>", focus_search)

