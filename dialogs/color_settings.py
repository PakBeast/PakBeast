"""Color settings dialog using CustomTkinter."""

import customtkinter as ctk
from tkinter.colorchooser import askcolor
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from core.settings import Settings

from ui.utils import set_window_icon


def show_color_settings_dialog(
    parent,
    settings: 'Settings',
    on_color_change: Callable[[], None]
) -> None:
    """Show the color settings dialog."""
    win = ctk.CTkToplevel(parent)
    win.title("Color Settings")
    win.transient(parent)
    win.resizable(False, False)
    win.minsize(500, 300)
    
    # Center window relative to parent (use explicit dimensions)
    win.update_idletasks()
    
    # Set icon after window is created and updated
    set_window_icon(win)
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    dialog_width = 500
    dialog_height = 300
    x = parent_x + (parent_width // 2) - (dialog_width // 2)
    y = parent_y + (parent_height // 2) - (dialog_height // 2)
    win.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    main_frame = ctk.CTkFrame(win, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    ctk.CTkLabel(
        main_frame,
        text="Customize syntax highlighting colors:",
        font=ctk.CTkFont(size=12)
    ).pack(anchor="w", pady=(0, 20))
    
    color_vars = {k: ctk.StringVar(value=v) for k, v in settings.colors.items()}
    
    def create_picker(key, label_text):
        """Create a color picker row."""
        row = ctk.CTkFrame(main_frame, fg_color="transparent")
        row.pack(fill="x", pady=10)
        
        label = ctk.CTkLabel(row, text=label_text, width=120, anchor="w")
        label.pack(side="left", padx=(0, 10))
        
        def pick_color():
            """Open color picker and update button."""
            color = askcolor(color_vars[key].get(), title=f"Select color for {label_text}")
            if color and color[1]:
                color_vars[key].set(color[1])
                btn.configure(fg_color=color[1])
        
        btn = ctk.CTkButton(
            row,
            text="Pick Color",
            command=pick_color,
            fg_color=color_vars[key].get(),
            width=120,
            height=30
        )
        btn.pack(side="left")
    
    create_picker("param", "Parameters:")
    create_picker("prop", "Properties:")
    create_picker("block_header", "Block Headers:")
    
    def save_colors():
        """Save color settings."""
        for key, var in color_vars.items():
            settings.colors[key] = var.get()
        settings.save()
        on_color_change()
        win.destroy()
    
    # Buttons
    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.pack(fill="x", pady=(20, 0))
    
    ctk.CTkButton(
        button_frame,
        text="Cancel",
        command=win.destroy,
        width=120,
        height=35
    ).pack(side="right", padx=(10, 0))
    
    ctk.CTkButton(
        button_frame,
        text="Save & Close",
        command=save_colors,
        width=120,
        height=35
    ).pack(side="right")
    
    win.grab_set()

