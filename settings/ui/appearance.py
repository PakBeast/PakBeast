"""Appearance settings tab builder."""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App


def build_appearance_tab(app: 'App', parent):
    """Build the appearance settings tab with modern design."""
    settings_container = ctk.CTkFrame(parent, fg_color="transparent")
    settings_container.pack(fill="both", expand=True, padx=16, pady=16)
    
    # Create scrollable frame
    scrollable = ctk.CTkScrollableFrame(settings_container)
    scrollable.pack(fill="both", expand=True, padx=0, pady=0)
    
    # Main header
    header_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
    header_frame.pack(fill="x", padx=0, pady=(0, 24))
    
    main_header = ctk.CTkLabel(
        header_frame,
        text="Appearance Settings",
        font=ctk.CTkFont(size=22, weight="bold"),
        text_color=("gray10", "gray90"),
    )
    main_header.pack(anchor="w")
    
    header_desc = ctk.CTkLabel(
        header_frame,
        text="Customize the editor's appearance and syntax highlighting colors",
        font=ctk.CTkFont(size=12),
        text_color=("gray40", "gray70"),
    )
    header_desc.pack(anchor="w", pady=(4, 0))
    
    # ===== EDITOR THEME SECTION =====
    theme_section = ctk.CTkFrame(
        scrollable,
        fg_color=("gray98", "gray18"),
        border_width=1,
        border_color=("gray80", "gray25"),
        corner_radius=12
    )
    theme_section.pack(fill="x", padx=0, pady=(0, 20))
    
    # Theme color variables
    theme_vars = {k: ctk.StringVar(value=v) for k, v in app.settings.theme.items()}
    theme_swatches = {}
    
    # Clickable header with expand/collapse
    theme_header_clickable = ctk.CTkFrame(theme_section, fg_color="transparent", cursor="hand2")
    theme_header_clickable.pack(fill="x", padx=18, pady=(18, 0))
    
    theme_header_content = ctk.CTkFrame(theme_header_clickable, fg_color="transparent")
    theme_header_content.pack(fill="x")
    
    # Expand/collapse arrow indicator
    theme_expanded = True
    theme_arrow = ctk.CTkLabel(
        theme_header_content,
        text="▼",
        font=ctk.CTkFont(size=12),
        text_color=("gray40", "gray70"),
        width=20
    )
    theme_arrow.pack(side="left", padx=(0, 8))
    
    theme_header = ctk.CTkLabel(
        theme_header_content,
        text="Editor Theme",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color=("gray10", "gray90"),
    )
    theme_header.pack(side="left")
    
    theme_desc = ctk.CTkLabel(
        theme_header_clickable,
        text="Configure the editor background, text, and edited line colors",
        font=ctk.CTkFont(size=11),
        text_color=("gray30", "gray80")
    )
    theme_desc.pack(anchor="w", padx=28, pady=(4, 12))
    
    # Content frame that can be shown/hidden
    theme_content_frame = ctk.CTkFrame(theme_section, fg_color="transparent")
    theme_content_frame.pack(fill="x", padx=0, pady=(0, 18))
    
    def toggle_theme_section():
        """Toggle theme section visibility."""
        nonlocal theme_expanded
        theme_expanded = not theme_expanded
        if theme_expanded:
            theme_content_frame.pack(fill="x", padx=0, pady=(0, 18))
            theme_arrow.configure(text="▼")
        else:
            theme_content_frame.pack_forget()
            theme_arrow.configure(text="▶")
    
    theme_header_clickable.bind("<Button-1>", lambda e: toggle_theme_section())
    theme_header_content.bind("<Button-1>", lambda e: toggle_theme_section())
    theme_arrow.bind("<Button-1>", lambda e: toggle_theme_section())
    theme_header.bind("<Button-1>", lambda e: toggle_theme_section())
    
    def create_theme_picker(key, label_text, description=""):
        """Create a theme color picker row."""
        picker_frame = ctk.CTkFrame(theme_content_frame, fg_color="transparent")
        picker_frame.pack(fill="x", padx=18, pady=(0, 16))
        
        # Left side: Label and description
        label_frame = ctk.CTkFrame(picker_frame, fg_color="transparent")
        label_frame.pack(side="left", fill="x", expand=True, padx=(0, 16))
        
        label = ctk.CTkLabel(
            label_frame,
            text=label_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        label.pack(anchor="w")
        
        if description:
            desc_label = ctk.CTkLabel(
                label_frame,
                text=description,
                font=ctk.CTkFont(size=11),
                text_color=("gray40", "gray70"),
                anchor="w"
            )
            desc_label.pack(anchor="w", pady=(2, 0))
        
        # Right side: Clickable color swatch
        def pick_color():
            """Open color picker and update swatch."""
            from tkinter.colorchooser import askcolor
            color = askcolor(
                theme_vars[key].get(),
                title=f"Select {label_text}"
            )
            if color and color[1]:
                theme_vars[key].set(color[1])
        
        # Color preview swatch (clickable button styled as swatch)
        preview_swatch = ctk.CTkButton(
            picker_frame,
            text="",
            command=pick_color,
            fg_color=theme_vars[key].get(),
            hover_color=theme_vars[key].get(),
            width=80,
            height=40,
            corner_radius=8,
            border_width=2,
            border_color=("gray75", "gray30"),
        )
        preview_swatch.pack(side="right")
        theme_swatches[key] = preview_swatch
        
        # Update preview when color changes
        def update_preview(*args):
            preview_swatch.configure(fg_color=theme_vars[key].get(), hover_color=theme_vars[key].get())
        theme_vars[key].trace_add("write", update_preview)
        
        return preview_swatch
    
    create_theme_picker("background", "Background", "Editor background color")
    create_theme_picker("foreground", "Text", "Default text color")
    create_theme_picker("edited_line", "Edited Lines", "Background color for lines with modifications")
    
    # ===== SYNTAX HIGHLIGHTING SECTION =====
    syntax_section = ctk.CTkFrame(
        scrollable,
        fg_color=("gray98", "gray18"),
        border_width=1,
        border_color=("gray80", "gray25"),
        corner_radius=12
    )
    syntax_section.pack(fill="x", padx=0, pady=(0, 20))
    
    # Syntax color variables
    color_vars = {k: ctk.StringVar(value=v) for k, v in app.settings.colors.items()}
    color_swatches = {}
    
    # Clickable header with expand/collapse
    syntax_header_clickable = ctk.CTkFrame(syntax_section, fg_color="transparent", cursor="hand2")
    syntax_header_clickable.pack(fill="x", padx=18, pady=(18, 0))
    
    syntax_header_content = ctk.CTkFrame(syntax_header_clickable, fg_color="transparent")
    syntax_header_content.pack(fill="x")
    
    # Expand/collapse arrow indicator
    syntax_expanded = True
    syntax_arrow = ctk.CTkLabel(
        syntax_header_content,
        text="▼",
        font=ctk.CTkFont(size=12),
        text_color=("gray40", "gray70"),
        width=20
    )
    syntax_arrow.pack(side="left", padx=(0, 8))
    
    syntax_header = ctk.CTkLabel(
        syntax_header_content,
        text="Syntax Highlighting",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color=("gray10", "gray90"),
    )
    syntax_header.pack(side="left")
    
    syntax_desc = ctk.CTkLabel(
        syntax_header_clickable,
        text="Customize colors for different code elements",
        font=ctk.CTkFont(size=11),
        text_color=("gray30", "gray80")
    )
    syntax_desc.pack(anchor="w", padx=28, pady=(4, 12))
    
    # Content frame that can be shown/hidden
    syntax_content_frame = ctk.CTkFrame(syntax_section, fg_color="transparent")
    syntax_content_frame.pack(fill="x", padx=0, pady=(0, 18))
    
    def toggle_syntax_section():
        """Toggle syntax section visibility."""
        nonlocal syntax_expanded
        syntax_expanded = not syntax_expanded
        if syntax_expanded:
            syntax_content_frame.pack(fill="x", padx=0, pady=(0, 18))
            syntax_arrow.configure(text="▼")
        else:
            syntax_content_frame.pack_forget()
            syntax_arrow.configure(text="▶")
    
    syntax_header_clickable.bind("<Button-1>", lambda e: toggle_syntax_section())
    syntax_header_content.bind("<Button-1>", lambda e: toggle_syntax_section())
    syntax_arrow.bind("<Button-1>", lambda e: toggle_syntax_section())
    syntax_header.bind("<Button-1>", lambda e: toggle_syntax_section())
    
    def create_syntax_picker(key, label_text, description=""):
        """Create a syntax color picker row."""
        picker_frame = ctk.CTkFrame(syntax_content_frame, fg_color="transparent")
        picker_frame.pack(fill="x", padx=18, pady=(0, 16))
        
        # Left side: Label and description
        label_frame = ctk.CTkFrame(picker_frame, fg_color="transparent")
        label_frame.pack(side="left", fill="x", expand=True, padx=(0, 16))
        
        label = ctk.CTkLabel(
            label_frame,
            text=label_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        label.pack(anchor="w")
        
        if description:
            desc_label = ctk.CTkLabel(
                label_frame,
                text=description,
                font=ctk.CTkFont(size=11),
                text_color=("gray40", "gray70"),
                anchor="w"
            )
            desc_label.pack(anchor="w", pady=(2, 0))
        
        # Right side: Clickable color swatch
        def pick_color():
            """Open color picker and update swatch."""
            from tkinter.colorchooser import askcolor
            color = askcolor(
                color_vars[key].get(),
                title=f"Select Color for {label_text}"
            )
            if color and color[1]:
                color_vars[key].set(color[1])
        
        # Color preview swatch (clickable button styled as swatch)
        preview_swatch = ctk.CTkButton(
            picker_frame,
            text="",
            command=pick_color,
            fg_color=color_vars[key].get(),
            hover_color=color_vars[key].get(),
            width=80,
            height=40,
            corner_radius=8,
            border_width=2,
            border_color=("gray75", "gray30"),
        )
        preview_swatch.pack(side="right")
        color_swatches[key] = preview_swatch
        
        # Update preview when color changes
        def update_preview(*args):
            preview_swatch.configure(fg_color=color_vars[key].get(), hover_color=color_vars[key].get())
        color_vars[key].trace_add("write", update_preview)
        
        return preview_swatch
    
    create_syntax_picker("param", "Parameters", "Function and method parameters")
    create_syntax_picker("prop", "Properties", "Object properties and attributes")
    create_syntax_picker("block_header", "Block Headers", "Block and section headers")
    create_syntax_picker("string", "Strings", "String literals")
    create_syntax_picker("number", "Numbers", "Numeric values")
    create_syntax_picker("comment", "Comments", "Code comments")
    
    # ===== ACTION BUTTONS SECTION =====
    button_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
    button_frame.pack(fill="x", padx=0, pady=(8, 0))
    
    def reset_to_defaults():
        """Reset all colors to default values."""
        # Reset theme defaults
        theme_defaults = {
            "background": "#1e1e1e",
            "foreground": "#d4d4d4",
            "edited_line": "#2a3a3a",
        }
        
        # Reset syntax defaults
        syntax_defaults = {
            "param": "#569cd6",      # Bright blue - excellent for parameters/functions
            "prop": "#4ec9b0",       # Cyan - distinct for properties/attributes
            "block_header": "#c586c0", # Purple - stands out for block headers/sections
            "string": "#ce9178",     # Warm orange - perfect for string literals
            "number": "#b5cea8",     # Light green - clear for numeric values
            "comment": "#6a9955",    # Muted green - traditional comment color
        }
        
        # Reset theme colors
        for key in theme_vars:
            default_color = theme_defaults[key]
            theme_vars[key].set(default_color)
            if key in theme_swatches:
                theme_swatches[key].configure(fg_color=default_color, hover_color=default_color)
        
        # Reset syntax colors
        for key in color_vars:
            default_color = syntax_defaults[key]
            color_vars[key].set(default_color)
            if key in color_swatches:
                color_swatches[key].configure(fg_color=default_color, hover_color=default_color)
        
        # Apply immediately
        from editor.operations import preview_handler
        for key, var in theme_vars.items():
            app.settings.theme[key] = var.get()
        for key, var in color_vars.items():
            app.settings.colors[key] = var.get()
        preview_handler.configure_text_tags(app)
        app._apply_syntax_highlighting()
    
    def save_all_settings():
        """Save all appearance settings."""
        # Save theme colors
        for key, var in theme_vars.items():
            app.settings.theme[key] = var.get()
        
        # Save syntax colors
        for key, var in color_vars.items():
            app.settings.colors[key] = var.get()
        
        app.settings.save()
        
        # Apply changes
        from editor.operations import preview_handler
        preview_handler.configure_text_tags(app)
        app._apply_syntax_highlighting()
        
        if hasattr(app, '_update_status'):
            app._update_status("Appearance settings saved successfully", "#4CAF50")
        else:
            app.status.set("Appearance settings saved successfully")
    
    # Button container with spacing
    buttons_container = ctk.CTkFrame(button_frame, fg_color="transparent")
    buttons_container.pack(anchor="w", padx=0, pady=0)
    
    reset_btn = ctk.CTkButton(
        buttons_container,
        text="Reset to Defaults",
        command=reset_to_defaults,
        width=160,
        height=40,
        font=ctk.CTkFont(size=13, weight="bold"),
        corner_radius=8,
        fg_color=("gray70", "gray35"),
        hover_color=("gray60", "gray45"),
        border_width=1,
        border_color=("gray75", "gray30"),
    )
    reset_btn.pack(side="left", padx=(0, 12))
    
    save_btn = ctk.CTkButton(
        buttons_container,
        text="Save Changes",
        command=save_all_settings,
        width=160,
        height=40,
        font=ctk.CTkFont(size=13, weight="bold"),
        corner_radius=8,
        fg_color=("gray85", "gray25"),
        hover_color=("gray75", "gray35"),
        border_width=1,
        border_color=("gray75", "gray30"),
    )
    save_btn.pack(side="left")
