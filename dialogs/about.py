"""About/Help dialog using CustomTkinter."""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.settings import Settings

from core.constants import APP_NAME
from ui.utils import set_window_icon


def show_about_dialog(parent, settings: 'Settings') -> None:
    """Show the About dialog window."""
    win = ctk.CTkToplevel(parent)
    win.title("About & Help")
    win.transient(parent)
    win.resizable(False, False)
    win.minsize(600, 500)
    
    # Center window relative to parent (use explicit dimensions)
    win.update_idletasks()
    
    # Set icon after window is created and updated
    set_window_icon(win)
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    dialog_width = 600
    dialog_height = 500
    x = parent_x + (parent_width // 2) - (dialog_width // 2)
    y = parent_y + (parent_height // 2) - (dialog_height // 2)
    win.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    main_frame = ctk.CTkFrame(win, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    title_label = ctk.CTkLabel(
        main_frame,
        text=APP_NAME,
        font=ctk.CTkFont(size=18, weight="bold")
    )
    title_label.pack(anchor="w", pady=(0, 10))
    
    subtitle_label = ctk.CTkLabel(
        main_frame,
        text="A tool for modifying Dying Light .scr files.",
        font=ctk.CTkFont(size=12)
    )
    subtitle_label.pack(anchor="w", pady=(0, 20))
    
    # Scrollable frame for content
    scrollable_frame = ctk.CTkScrollableFrame(main_frame)
    scrollable_frame.pack(fill="both", expand=True, pady=(0, 20))
    
    help_text = {
        "Params": 'e.g., Param("MaxAmmo", 30);\nThese are named values. Double-click to edit the value.',
        "Properties": 'e.g., Price(1500);\nThese are often found inside Item definitions. Double-click to edit the value.',
        "Blocks": 'e.g., AttackPreset("biter_grab") { ... }\nThese are multi-line blocks of code. You can search for them and mark the entire block for deletion from the search results, or by double-clicking the header line in the preview.'
    }
    
    for title, text in help_text.items():
        section_title = ctk.CTkLabel(
            scrollable_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        section_title.pack(anchor="w", pady=(10, 5))
        
        section_text = ctk.CTkLabel(
            scrollable_frame,
            text=text,
            font=ctk.CTkFont(size=11),
            justify="left",
            anchor="w"
        )
        section_text.pack(anchor="w", padx=(0, 20))
    
    # Close button
    ctk.CTkButton(
        main_frame,
        text="Close",
        command=win.destroy,
        width=120,
        height=35
    ).pack(pady=(10, 0))
    
    win.grab_set()

