"""Settings tabs building functions."""

import customtkinter as ctk
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App


def build_general_settings_tab(app: 'App', parent):
    """Build the general settings tab."""
    settings_container = ctk.CTkFrame(parent, fg_color="transparent")
    settings_container.pack(fill="both", expand=True, padx=16, pady=(12, 16))
    
    # Create scrollable frame
    scrollable = ctk.CTkScrollableFrame(settings_container)
    scrollable.pack(fill="both", expand=True, padx=0, pady=(0, 16))
    
    # Header Section
    header_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
    header_frame.pack(fill="x", padx=12, pady=(12, 25))
    
    header = ctk.CTkLabel(
        header_frame,
        text="General Settings",
        font=ctk.CTkFont(size=18, weight="bold")
    )
    header.pack(anchor="w")
    
    # Default Directory Section
    dir_section = ctk.CTkFrame(
        scrollable,
        fg_color=("gray95", "gray20"),
        border_width=1,
        border_color=("gray80", "gray30"),
        corner_radius=8
    )
    dir_section.pack(fill="x", padx=12, pady=(0, 20))
    
    section_header = ctk.CTkLabel(
        dir_section,
        text="Default Directory",
        font=ctk.CTkFont(size=14, weight="bold")
    )
    section_header.pack(anchor="w", padx=16, pady=(16, 8))
    
    section_desc = ctk.CTkLabel(
        dir_section,
        text="Default folder location for opening and saving files",
        font=ctk.CTkFont(size=11),
        text_color=("white", "white")
    )
    section_desc.pack(anchor="w", padx=16, pady=(0, 12))
    
    folder_input_frame = ctk.CTkFrame(dir_section, fg_color="transparent")
    folder_input_frame.pack(fill="x", padx=16, pady=(0, 16))
    
    v_last = ctk.StringVar(value=app.settings.last_pak_dir)
    folder_entry = ctk.CTkEntry(
        folder_input_frame,
        textvariable=v_last,
        placeholder_text="Select default directory...",
        height=36,
        font=ctk.CTkFont(size=13)
    )
    folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
    
    def pick_dir():
        from tkinter import filedialog
        if p := filedialog.askdirectory(title="Select Default Directory"):
            v_last.set(p)
    
    ctk.CTkButton(
        folder_input_frame,
        text="Browse...",
        command=pick_dir,
        width=110,
        height=36,
        font=ctk.CTkFont(size=13, weight="bold")
    ).pack(side="left")
    
    # Save Button Section
    button_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
    button_frame.pack(fill="x", padx=12, pady=(0, 30))
    
    def save_general():
        app.settings.last_pak_dir = v_last.get().strip() or app.settings.last_pak_dir
        app.settings.save()
        if hasattr(app, '_update_status'):
            app._update_status("Settings saved successfully", "#4CAF50")
        else:
            app.status.set("Settings saved successfully")
    
    save_btn = ctk.CTkButton(
        button_frame,
        text="Save Changes",
        command=save_general,
        width=140,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold"),
        corner_radius=6
    )
    save_btn.pack(anchor="w")


def build_multi_packer_tab(app: 'App', parent):
    """Build the multi-packer settings tab."""
    settings_container = ctk.CTkFrame(parent, fg_color="transparent")
    settings_container.pack(fill="both", expand=True, padx=16, pady=(12, 16))
    
    # Create scrollable frame
    scrollable = ctk.CTkScrollableFrame(settings_container)
    scrollable.pack(fill="both", expand=True, padx=0, pady=(0, 16))
    
    # Header Section
    header_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
    header_frame.pack(fill="x", padx=12, pady=(12, 25))
    
    packer_header = ctk.CTkLabel(
        header_frame,
        text="Multi-Packer Configuration",
        font=ctk.CTkFont(size=18, weight="bold")
    )
    packer_header.pack(anchor="w")
    
    # File List Section
    files_section = ctk.CTkFrame(
        scrollable,
        fg_color=("gray95", "gray20"),
        border_width=1,
        border_color=("gray80", "gray30"),
        corner_radius=8
    )
    files_section.pack(fill="both", expand=True, padx=12, pady=(0, 20))
    
    section_header = ctk.CTkLabel(
        files_section,
        text="Additional .pak Files",
        font=ctk.CTkFont(size=14, weight="bold")
    )
    section_header.pack(anchor="w", padx=16, pady=(16, 8))
    
    section_desc = ctk.CTkLabel(
        files_section,
        text="Additional .pak files to merge during compilation (processed top to bottom)",
        font=ctk.CTkFont(size=11),
        text_color=("white", "white")
    )
    section_desc.pack(anchor="w", padx=16, pady=(0, 12))
    
    # Scrollable list container
    list_container = ctk.CTkFrame(files_section, fg_color="transparent")
    list_container.pack(fill="both", expand=True, padx=16, pady=(0, 12))
    
    scrollable_list = ctk.CTkScrollableFrame(
        list_container,
        border_width=1,
        border_color=("gray85", "gray25"),
        corner_radius=6
    )
    scrollable_list.pack(fill="both", expand=True)
    
    # Store list items reference in app for updates
    app.multi_pack_list_items = []
    for idx, f in enumerate(app.settings.multi_pack_files, 1):
        item_frame = ctk.CTkFrame(
            scrollable_list,
            fg_color=("gray90", "gray18"),
            corner_radius=4
        )
        item_frame.pack(fill="x", pady=3, padx=5)
        
        # Number label
        num_label = ctk.CTkLabel(
            item_frame,
            text=f"{idx}.",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=25,
            anchor="w"
        )
        num_label.pack(side="left", padx=(10, 8))
        
        # File path label
        label = ctk.CTkLabel(
            item_frame,
            text=f,
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        label.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        app.multi_pack_list_items.append((item_frame, label, f))
    
    # Action buttons
    btn_frame = ctk.CTkFrame(files_section, fg_color="transparent")
    btn_frame.pack(fill="x", padx=16, pady=(0, 16))
    
    def add_pak():
        """Add pak files to the list."""
        from tkinter import filedialog
        files = filedialog.askopenfilenames(
            title="Select .pak Files",
            filetypes=[("PAK Files", "*.pak"), ("All files", "*.*")],
            initialdir=app.settings.last_pak_dir
        )
        if files:
            start_idx = len(app.multi_pack_list_items) + 1
            for idx, f in enumerate(files, start=start_idx):
                if f not in [item[2] for item in app.multi_pack_list_items]:
                    item_frame = ctk.CTkFrame(
                        scrollable_list,
                        fg_color=("gray90", "gray18"),
                        corner_radius=4
                    )
                    item_frame.pack(fill="x", pady=3, padx=5)
                    
                    num_label = ctk.CTkLabel(
                        item_frame,
                        text=f"{len(app.multi_pack_list_items) + 1}.",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        width=25,
                        anchor="w"
                    )
                    num_label.pack(side="left", padx=(10, 8))
                    
                    label = ctk.CTkLabel(
                        item_frame,
                        text=f,
                        anchor="w",
                        font=ctk.CTkFont(size=12)
                    )
                    label.pack(side="left", fill="x", expand=True, padx=(0, 10))
                    
                    app.multi_pack_list_items.append((item_frame, label, f))
            app.settings.last_pak_dir = str(Path(files[0]).parent)
    
    def remove_pak():
        """Remove last pak file from the list."""
        if app.multi_pack_list_items:
            item_frame, label, f = app.multi_pack_list_items.pop()
            item_frame.destroy()
    
    ctk.CTkButton(
        btn_frame,
        text="Add Files",
        command=add_pak,
        width=120,
        height=36,
        font=ctk.CTkFont(size=13, weight="bold")
    ).pack(side="left", padx=(0, 10))
    
    ctk.CTkButton(
        btn_frame,
        text="Remove Last",
        command=remove_pak,
        width=120,
        height=36,
        font=ctk.CTkFont(size=13, weight="bold")
    ).pack(side="left")
    
    # Conflict Resolution Section
    conflict_section = ctk.CTkFrame(
        scrollable,
        fg_color=("gray95", "gray20"),
        border_width=1,
        border_color=("gray80", "gray30"),
        corner_radius=8
    )
    conflict_section.pack(fill="x", padx=12, pady=(0, 25))
    
    policy_label = ctk.CTkLabel(
        conflict_section,
        text="File Conflict Resolution",
        font=ctk.CTkFont(size=14, weight="bold")
    )
    policy_label.pack(anchor="w", padx=16, pady=(16, 8))
    
    policy_desc = ctk.CTkLabel(
        conflict_section,
        text="How to handle files that exist in multiple .pak files",
        font=ctk.CTkFont(size=11),
        text_color=("white", "white")
    )
    policy_desc.pack(anchor="w", padx=16, pady=(0, 12))
    
    overwrite_var = ctk.StringVar(value="overwrite" if app.settings.multi_pack_overwrite else "keep")
    
    radio_frame = ctk.CTkFrame(conflict_section, fg_color="transparent")
    radio_frame.pack(fill="x", padx=16, pady=(0, 16))
    
    ctk.CTkRadioButton(
        radio_frame,
        text="Overwrite existing files",
        variable=overwrite_var,
        value="overwrite",
        font=ctk.CTkFont(size=12)
    ).pack(anchor="w", pady=(0, 8))
    
    ctk.CTkRadioButton(
        radio_frame,
        text="Keep existing files",
        variable=overwrite_var,
        value="keep",
        font=ctk.CTkFont(size=12)
    ).pack(anchor="w")
    
    # Save Button Section
    button_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
    button_frame.pack(fill="x", padx=12, pady=(0, 20))
    
    def save_packer_settings():
        """Save packer settings."""
        app.settings.multi_pack_files = [item[2] for item in app.multi_pack_list_items]
        app.settings.multi_pack_overwrite = overwrite_var.get() == "overwrite"
        app.settings.save()
        if hasattr(app, '_update_status'):
            app._update_status("Multi-Packer settings saved successfully", "#4CAF50")
        else:
            app.status.set("Multi-Packer settings saved successfully")
    
    packer_save_btn = ctk.CTkButton(
        button_frame,
        text="Save Changes",
        command=save_packer_settings,
        width=140,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold"),
        corner_radius=6
    )
    packer_save_btn.pack(anchor="w")


def build_colors_tab(app: 'App', parent):
    """Build the colors settings tab."""
    settings_container = ctk.CTkFrame(parent, fg_color="transparent")
    settings_container.pack(fill="both", expand=True, padx=16, pady=(12, 16))
    
    # Create scrollable frame
    scrollable = ctk.CTkScrollableFrame(settings_container)
    scrollable.pack(fill="both", expand=True, padx=0, pady=(0, 16))
    
    # Header Section
    header_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
    header_frame.pack(fill="x", padx=12, pady=(12, 25))
    
    color_header = ctk.CTkLabel(
        header_frame,
        text="Syntax Highlighting",
        font=ctk.CTkFont(size=18, weight="bold")
    )
    color_header.pack(anchor="w")
    
    # Color Picker Section
    colors_section = ctk.CTkFrame(
        scrollable,
        fg_color=("gray95", "gray20"),
        border_width=1,
        border_color=("gray80", "gray30"),
        corner_radius=8
    )
    colors_section.pack(fill="x", padx=12, pady=(0, 25))
    
    section_header = ctk.CTkLabel(
        colors_section,
        text="Colors",
        font=ctk.CTkFont(size=14, weight="bold")
    )
    section_header.pack(anchor="w", padx=16, pady=(16, 8))
    
    section_desc = ctk.CTkLabel(
        colors_section,
        text="Customize syntax highlighting colors for code elements",
        font=ctk.CTkFont(size=11),
        text_color=("white", "white")
    )
    section_desc.pack(anchor="w", padx=16, pady=(0, 12))
    
    # Use dark mode colors (custom theme)
    color_vars = {k: ctk.StringVar(value=v) for k, v in app.settings.colors["dark"].items()}
    color_buttons = {}
    
    def create_picker(key, label_text):
        """Create a color picker row."""
        picker_frame = ctk.CTkFrame(colors_section, fg_color="transparent")
        picker_frame.pack(fill="x", padx=16, pady=(0, 16))
        
        # Label
        label_frame = ctk.CTkFrame(picker_frame, fg_color="transparent")
        label_frame.pack(side="left", fill="x", expand=True, padx=(0, 16))
        
        label = ctk.CTkLabel(
            label_frame,
            text=label_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        label.pack(anchor="w")
        
        def pick_color():
            """Open color picker and update button."""
            from tkinter.colorchooser import askcolor
            color = askcolor(
                color_vars[key].get(),
                title=f"Select Color for {label_text.replace(':', '')}"
            )
            if color and color[1]:
                color_vars[key].set(color[1])
                btn.configure(fg_color=color[1], hover_color=color[1])
        
        btn = ctk.CTkButton(
            picker_frame,
            text="Choose Color",
            command=pick_color,
            fg_color=color_vars[key].get(),
            hover_color=color_vars[key].get(),
            width=140,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=6
        )
        btn.pack(side="right")
        color_buttons[key] = btn
        return btn
    
    create_picker("param", "Parameters")
    create_picker("prop", "Properties")
    create_picker("block_header", "Block Headers")
    
    # Save Button Section
    button_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
    button_frame.pack(fill="x", padx=12, pady=(0, 12))
    
    # Reset to Defaults button
    def reset_to_defaults():
        """Reset colors to default values."""
        defaults = {
            "param": "#4fc3f7",
            "prop": "#26c6da",
            "block_header": "#ba68c8",
        }
        
        for key in color_vars:
            default_color = defaults[key]
            color_vars[key].set(default_color)
            if key in color_buttons:
                color_buttons[key].configure(fg_color=default_color, hover_color=default_color)
        
        # Apply immediately
        from operations import preview_handler
        for key, var in color_vars.items():
            app.settings.colors["dark"][key] = var.get()
        preview_handler.configure_text_tags(app)
        app._apply_syntax_highlighting()
    
    def save_colors():
        """Save color settings."""
        for key, var in color_vars.items():
            app.settings.colors["dark"][key] = var.get()
        app.settings.save()
        from operations import preview_handler
        preview_handler.configure_text_tags(app)
        app._apply_syntax_highlighting()
        if hasattr(app, '_update_status'):
            app._update_status("Color settings saved successfully", "#4CAF50")
        else:
            app.status.set("Color settings saved successfully")
    
    reset_btn = ctk.CTkButton(
        button_frame,
        text="Reset to Defaults",
        command=reset_to_defaults,
        width=150,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold"),
        corner_radius=6,
        fg_color=("gray60", "gray40"),
        hover_color=("gray50", "gray50")
    )
    reset_btn.pack(side="left", padx=(0, 10))
    
    color_save_btn = ctk.CTkButton(
        button_frame,
        text="Save Changes",
        command=save_colors,
        width=140,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold"),
        corner_radius=6
    )
    color_save_btn.pack(side="left")

