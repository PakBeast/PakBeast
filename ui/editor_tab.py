"""Editor tab building functions."""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App

from .utils import is_dark_mode, get_listbox_colors, get_preview_colors


def build_editor_tab(app: 'App', parent):
    """Build the editor tab with left sidebar tabs and right preview panel."""
    editor_container = ctk.CTkFrame(parent, fg_color="transparent")
    editor_container.pack(fill="both", expand=True, padx=8, pady=8)
    
    # Left sidebar with tabs: Files | Search & Modifications
    left_sidebar = ctk.CTkFrame(editor_container, fg_color="transparent")
    left_sidebar.pack(side="left", fill="both", expand=False, padx=(0, 12))
    # Set fixed width for left sidebar - increased for better visibility of long strings
    left_sidebar.configure(width=650)
    left_sidebar.pack_propagate(False)
    
    # Create tabview for left sidebar
    sidebar_tabs = ctk.CTkTabview(left_sidebar)
    sidebar_tabs.pack(fill="both", expand=True)
    
    # Tab 1: Project Files
    files_tab = sidebar_tabs.add("Files")
    explorer_panel = ctk.CTkFrame(files_tab, fg_color="transparent", border_width=1, border_color=("gray70", "gray30"), corner_radius=8)
    explorer_panel.pack(fill="both", expand=True)
    _build_file_explorer(app, explorer_panel)
    
    # Tab 2: Search & Modifications (combined in one tab)
    search_edits_tab = sidebar_tabs.add("Search & Modifications")
    
    # Search Panel (top half)
    search_panel = ctk.CTkFrame(search_edits_tab, fg_color="transparent", border_width=1, border_color=("gray70", "gray30"), corner_radius=8)
    search_panel.pack(fill="both", expand=True, pady=(0, 8))
    _build_search_panel(app, search_panel)
    
    # Active Modifications Panel (bottom half)
    edits_panel = ctk.CTkFrame(search_edits_tab, fg_color="transparent", border_width=1, border_color=("gray70", "gray30"), corner_radius=8)
    edits_panel.pack(fill="both", expand=True)
    _build_edits_panel(app, edits_panel)
    
    # Right side: Preview Panel (takes remaining space)
    preview_panel = ctk.CTkFrame(editor_container, fg_color="transparent", border_width=1, border_color=("gray70", "gray30"), corner_radius=8)
    preview_panel.pack(side="left", fill="both", expand=True)
    
    _build_preview_panel(app, preview_panel)


def _build_file_explorer(app: 'App', parent):
    """Build the file explorer panel."""
    # File Explorer Header
    explorer_header = ctk.CTkFrame(parent, fg_color="transparent")
    explorer_header.pack(fill="x", padx=10, pady=(8, 6))
    
    explorer_title = ctk.CTkLabel(
        explorer_header,
        text="Project Files",
        font=ctk.CTkFont(size=13, weight="bold")
    )
    explorer_title.pack(side="left")
    
    # File search
    app.file_search_var = ctk.StringVar()
    app.file_search_entry = ctk.CTkEntry(
        parent,
        textvariable=app.file_search_var,
        placeholder_text="Search files by name...",
        height=30,
        font=ctk.CTkFont(size=11),
        corner_radius=6
    )
    app.file_search_entry.pack(fill="x", padx=10, pady=(0, 8))
    app.file_search_var.trace_add("write", lambda *args: app._on_file_search_change(*args))
    
    # File tree - use tkinter Treeview with CustomTkinter styling
    tree_frame = ctk.CTkFrame(parent, fg_color="transparent")
    tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 8))
    
    # Style the treeview to match CustomTkinter theme
    style = ttk.Style()
    dark = is_dark_mode()
    if dark:
        style.theme_use("clam")
        style.configure("Treeview", 
                       background="#212121",
                       foreground="#FFFFFF",
                       fieldbackground="#212121",
                       borderwidth=0)
        style.map("Treeview", background=[("selected", "#1f538d")])
    else:
        style.theme_use("clam")
        style.configure("Treeview",
                       background="#FFFFFF",
                       foreground="#000000",
                       fieldbackground="#FFFFFF",
                       borderwidth=0)
        style.map("Treeview", background=[("selected", "#0078d4")])
    
    app.tree = ttk.Treeview(
        tree_frame,
        columns=("abspath", "tooltip"),
        show="tree",
        selectmode="browse"
    )
    app.tree.column("#0", width=200, minwidth=100)
    app.tree.column("abspath", width=0, stretch=False)  # Hidden, but stored
    app.tree.column("tooltip", width=0, stretch=False)  # Hidden, but stored
    app.tree.pack(side="left", fill="both", expand=True)
    
    scrollbar = ctk.CTkScrollbar(tree_frame, command=app.tree.yview, orientation="vertical")
    scrollbar.pack(side="right", fill="y")
    app.tree.configure(yscrollcommand=scrollbar.set)
    app.tree.bind("<<TreeviewSelect>>", app._on_tree_select)
    
    # Add tooltip on hover
    def on_tree_hover(event):
        """Show tooltip with full relative path on hover."""
        item = app.tree.identify_row(event.y)
        if item:
            tooltip_text = app.tree.set(item, "tooltip")
            if tooltip_text:
                # Create tooltip (using Tkinter tooltip or simple label)
                # For now, we'll use the status bar to show the path
                app.status.set(f"Path: {tooltip_text}")
    
    def on_tree_leave(event):
        """Clear tooltip on leave."""
        app.status.set("Ready")
    
    app.tree.bind("<Motion>", on_tree_hover)
    app.tree.bind("<Leave>", on_tree_leave)


def _build_search_panel(app: 'App', parent):
    """Build the search panel."""
    # Parent is already the panel frame, so build directly in it
    search_panel = parent
    
    # Search Header
    search_header = ctk.CTkFrame(search_panel, fg_color="transparent")
    search_header.pack(fill="x", padx=10, pady=(8, 6))
    
    search_title = ctk.CTkLabel(
        search_header,
        text="Parameter Search",
        font=ctk.CTkFont(size=13, weight="bold")
    )
    search_title.pack(side="left")
    
    # Search input
    search_input_frame = ctk.CTkFrame(search_panel, fg_color="transparent")
    search_input_frame.pack(fill="x", padx=10, pady=(0, 6))
    
    app.search_var = ctk.StringVar()
    app.ent_search = ctk.CTkEntry(
        search_input_frame,
        textvariable=app.search_var,
        placeholder_text="Enter search criteria...",
        height=30,
        font=ctk.CTkFont(size=11),
        corner_radius=6
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
        corner_radius=6
    )
    app.find_btn.pack(side="left")
    
    # Results hint - enhanced with better styling
    hint_frame = ctk.CTkFrame(
        search_panel,
        fg_color=("gray95", "gray20"),
        corner_radius=4,
        border_width=1,
        border_color=("gray85", "gray30")
    )
    hint_frame.pack(fill="x", padx=10, pady=(0, 6))
    
    results_hint = ctk.CTkLabel(
        hint_frame,
        text="💡 Tip: Click a result to preview • Double-click to add to modifications",
        font=ctk.CTkFont(size=10),
        text_color=("gray30", "gray80"),
        anchor="w",
        justify="left"
    )
    results_hint.pack(fill="x", padx=8, pady=6)
    
    # Results list
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
        activestyle="none"
    )
    app.lst_results.pack(side="left", fill="both", expand=True)
    
    results_scrollbar = ctk.CTkScrollbar(results_container, command=app.lst_results.yview, orientation="vertical")
    results_scrollbar.pack(side="right", fill="y")
    app.lst_results.configure(yscrollcommand=results_scrollbar.set)
    app.lst_results.bind("<Double-Button-1>", app._on_add_from_result)
    app.lst_results.bind("<ButtonRelease-1>", app._on_result_select)


def _build_edits_panel(app: 'App', parent):
    """Build the active edits panel."""
    # Parent is already the panel frame, so build directly in it
    edits_panel = parent
    
    # Edits Header
    edits_header = ctk.CTkFrame(edits_panel, fg_color="transparent")
    edits_header.pack(fill="x", padx=10, pady=(8, 6))
    
    edits_title = ctk.CTkLabel(
        edits_header,
        text="Active Modifications",
        font=ctk.CTkFont(size=13, weight="bold")
    )
    edits_title.pack(side="left")
    
    # Top row: Search bar and Actions button
    search_actions_frame = ctk.CTkFrame(edits_panel, fg_color="transparent")
    search_actions_frame.pack(fill="x", padx=10, pady=(0, 6))
    
    # Search edits entry
    app.search_edits_var = ctk.StringVar()
    app.search_edits_entry = ctk.CTkEntry(
        search_actions_frame,
        textvariable=app.search_edits_var,
        placeholder_text="Filter modifications...",
        height=30,
        font=ctk.CTkFont(size=11)
    )
    app.search_edits_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
    app.search_edits_var.trace_add("write", lambda *args: app._on_filter_change_debounced(*args))
    
    # Actions button with menu
    import tkinter as tk
    actions_btn = ctk.CTkButton(
        search_actions_frame,
        text="Actions",
        width=80,
        height=30,
        font=ctk.CTkFont(size=11)
    )
    actions_btn.pack(side="left")
    
    def show_actions_menu(event=None):
        """Show actions context menu."""
        menu = tk.Menu(app, tearoff=0)
        menu.add_command(label="Enable All Filtered", command=lambda: app._enable_all_filtered())
        menu.add_command(label="Disable All Filtered", command=lambda: app._disable_all_filtered())
        menu.add_separator()
        menu.add_command(label="Clear All Modifications", command=lambda: app._clear_edits())
        
        # Position menu below the Actions button
        try:
            actions_btn.update_idletasks()
            button_x = actions_btn.winfo_rootx()
            button_y = actions_btn.winfo_rooty() + actions_btn.winfo_height()
            menu.post(button_x, button_y)
        except:
            # Fallback positioning at cursor
            menu.post(app.winfo_pointerx(), app.winfo_pointery())
    
    actions_btn.configure(command=show_actions_menu)
    
    # Filter dropdowns (below search and actions)
    filter_frame = ctk.CTkFrame(edits_panel, fg_color="transparent")
    filter_frame.pack(fill="x", padx=10, pady=(0, 6))
    
    app.filter_edit_type = ctk.StringVar(value="All Edit Types")
    edit_types = ["All Edit Types", "VALUE_REPLACE", "BLOCK_DELETE", "LINE_DELETE", "LINE_REPLACE", "LINE_INSERT"]
    app.type_filter_combo = ctk.CTkComboBox(
        filter_frame,
        values=edit_types,
        variable=app.filter_edit_type,
        width=120,
        height=30,
        font=ctk.CTkFont(size=11),
        corner_radius=6,
        dropdown_font=ctk.CTkFont(size=11),
        state="readonly"
    )
    app.type_filter_combo.pack(side="left", padx=(0, 6))
    app.type_filter_combo.configure(command=lambda v: app._on_filter_change())
    
    app.filter_file_path = ctk.StringVar(value="All Files")
    app.file_filter_combo = ctk.CTkComboBox(
        filter_frame,
        values=["All Files"],
        variable=app.filter_file_path,
        width=120,
        height=30,
        font=ctk.CTkFont(size=11),
        corner_radius=6,
        dropdown_font=ctk.CTkFont(size=11),
        state="readonly"
    )
    app.file_filter_combo.pack(side="left", padx=(0, 6))
    app.file_filter_combo.configure(command=lambda v: app._on_filter_change())
    
    # Edits list
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
        activestyle="none"
    )
    app.lst_edits.pack(side="left", fill="both", expand=True)
    
    edits_scrollbar = ctk.CTkScrollbar(edits_container, command=app.lst_edits.yview, orientation="vertical")
    edits_scrollbar.pack(side="right", fill="y")
    app.lst_edits.configure(yscrollcommand=edits_scrollbar.set)
    app.lst_edits.bind("<Button-3>", app._edits_context)
    app.lst_edits.bind("<Double-Button-1>", lambda _e: app._toggle_selected_edit())
    app.lst_edits.bind("<ButtonRelease-1>", app._on_edit_select)


def _build_preview_panel(app: 'App', parent):
    """Build the preview panel."""
    # Preview Header
    preview_header = ctk.CTkFrame(parent, fg_color="transparent")
    preview_header.pack(fill="x", padx=10, pady=(8, 6))
    
    app.preview_label = ctk.CTkLabel(
        preview_header,
        text="File Preview: —",
        font=ctk.CTkFont(size=13, weight="bold")
    )
    app.preview_label.pack(side="left")
    
    # Preview text widget container with line numbers
    preview_container = ctk.CTkFrame(parent, fg_color="transparent")
    preview_container.pack(fill="both", expand=True, padx=10, pady=(0, 8))
    
    bg_color, fg_color, highlight_bg = get_preview_colors()
    is_dark = is_dark_mode()
    
    # Create frame to hold line numbers and text widget
    text_frame = tk.Frame(preview_container, bg=bg_color)
    text_frame.pack(side="left", fill="both", expand=True)
    
    # Line numbers widget
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
        insertbackground=fg_color
    )
    app.line_numbers.pack(side="left", fill="y")
    
    # Main text widget
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
        selectforeground=fg_color
    )
    app.txt.pack(side="left", fill="both", expand=True)
    
    # Configure hover tag for line highlighting
    hover_bg = "#2d2d30" if is_dark else "#e8e8e8"
    app.txt.tag_configure("hover", background=hover_bg)
    app.txt.tag_configure("highlight", background=highlight_bg)
    
    # Bind hover events
    def on_mouse_motion(event):
        """Handle mouse motion for line highlighting."""
        try:
            # Get line number at cursor position
            index = app.txt.index(f"@{event.x},{event.y}")
            line_num = index.split(".")[0]
            
            # Remove previous hover
            app.txt.tag_remove("hover", "1.0", "end")
            
            # Get the line content and check if it's empty
            line_start = f"{line_num}.0"
            line_end = f"{line_num}.end"
            line_content = app.txt.get(line_start, line_end).strip()
            
            # Only add hover if line is not empty
            if line_content:
                app.txt.tag_add("hover", line_start, line_end)
        except:
            pass
    
    def on_mouse_leave(event):
        """Remove hover highlight when mouse leaves."""
        app.txt.tag_remove("hover", "1.0", "end")
    
    app.txt.bind("<Motion>", on_mouse_motion)
    app.txt.bind("<Leave>", on_mouse_leave)
    
    # Prevent text selection - bind selection events to do nothing
    def prevent_selection(event):
        """Prevent any text selection in the preview."""
        return "break"
    
    app.txt.bind("<Button-1>", prevent_selection)
    app.txt.bind("<B1-Motion>", prevent_selection)
    app.txt.bind("<ButtonRelease-1>", prevent_selection)
    app.txt.bind("<Shift-Button-1>", prevent_selection)
    app.txt.bind("<Control-Button-1>", prevent_selection)
    
    # Update line numbers function
    def update_line_numbers():
        """Update line numbers display."""
        try:
            content = app.txt.get("1.0", "end-1c")
            line_count = len(content.splitlines())
            if content and not content.endswith('\n'):
                line_count += 1
            if line_count == 0:
                line_count = 1
            
            app.line_numbers.config(state="normal")
            app.line_numbers.delete("1.0", "end")
            for i in range(1, line_count + 1):
                app.line_numbers.insert("end", f"{i}\n")
            app.line_numbers.config(state="disabled")
            
            # Sync scroll position
            try:
                top = app.txt.yview()[0]
                app.line_numbers.yview_moveto(top)
            except:
                pass
        except:
            pass
    
    app._update_line_numbers = update_line_numbers
    
    # Scroll sync function
    def sync_scroll():
        """Sync scroll between text and line numbers."""
        try:
            top = app.txt.yview()[0]
            app.line_numbers.yview_moveto(top)
        except:
            pass
    
    # Create scrollbar first
    preview_scrollbar = ctk.CTkScrollbar(preview_container, orientation="vertical")
    preview_scrollbar.pack(side="right", fill="y")
    
    # Scrollbar command
    def scrollbar_command(*args):
        """Handle scrollbar scrolling."""
        app.txt.yview(*args)
        sync_scroll()
    
    # Text widget scroll command
    def text_scroll_command(*args):
        """Handle text widget scrolling."""
        sync_scroll()
        preview_scrollbar.set(*args)
    
    preview_scrollbar.configure(command=scrollbar_command)
    app.txt.configure(yscrollcommand=text_scroll_command)
    
    app.txt.bind("<Double-Button-1>", app._on_preview_double_click)
    app.txt.bind("<Button-3>", app._on_preview_right_click)

