"""Multi-Packer Settings dialog using CustomTkinter."""

import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.settings import Settings

from ui.utils import set_window_icon


def show_multi_packer_dialog(parent, settings: 'Settings') -> None:
    """Show the Multi-Packer Settings dialog window."""
    win = ctk.CTkToplevel(parent)
    win.title("Multi-Packer Settings")
    win.transient(parent)
    win.resizable(False, False)
    win.minsize(600, 550)
    
    # Center window relative to parent (use explicit dimensions)
    win.update_idletasks()
    
    # Set icon after window is created and updated
    set_window_icon(win)
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    dialog_width = 600
    dialog_height = 550
    x = parent_x + (parent_width // 2) - (dialog_width // 2)
    y = parent_y + (parent_height // 2) - (dialog_height // 2)
    win.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    main_frame = ctk.CTkFrame(win, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Header
    header_label = ctk.CTkLabel(
        main_frame,
        text="Multi-Packer Settings",
        font=ctk.CTkFont(size=16, weight="bold")
    )
    header_label.pack(anchor="w", pady=(0, 5))
    
    subtitle_label = ctk.CTkLabel(
        main_frame,
        text="Configure additional .pak files to merge during mod compilation.",
        font=ctk.CTkFont(size=11)
    )
    subtitle_label.pack(anchor="w", pady=(0, 15))
    
    # File list section
    list_label = ctk.CTkLabel(
        main_frame,
        text="Additional .pak Files (processed in order):",
        font=ctk.CTkFont(size=12, weight="bold")
    )
    list_label.pack(anchor="w", pady=(0, 10))
    
    # Scrollable listbox frame
    list_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    list_frame.pack(fill="both", expand=True, pady=(0, 15))
    
    # Use CTkScrollableFrame with labels as list items
    scrollable = ctk.CTkScrollableFrame(list_frame)
    scrollable.pack(fill="both", expand=True, padx=10, pady=10)
    
    list_items = []
    for f in settings.multi_pack_files:
        item_frame = ctk.CTkFrame(scrollable)
        item_frame.pack(fill="x", pady=2)
        label = ctk.CTkLabel(item_frame, text=f, anchor="w")
        label.pack(side="left", padx=10, fill="x", expand=True)
        list_items.append((item_frame, label, f))
    
    # Action buttons
    btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(0, 15))
    
    def add_pak():
        """Add pak files to the list."""
        files = filedialog.askopenfilenames(
            title="Select .pak files",
            filetypes=[("PAK files", "*.pak"), ("All files", "*.*")],
            initialdir=settings.last_pak_dir
        )
        if files:
            for f in files:
                if f not in [item[2] for item in list_items]:
                    item_frame = ctk.CTkFrame(scrollable)
                    item_frame.pack(fill="x", pady=2)
                    label = ctk.CTkLabel(item_frame, text=f, anchor="w")
                    label.pack(side="left", padx=10, fill="x", expand=True)
                    list_items.append((item_frame, label, f))
            settings.last_pak_dir = str(Path(files[0]).parent)
    
    def remove_pak():
        """Remove selected pak file from the list."""
        # Simple implementation: remove last item
        # In a full implementation, you'd track selection
        if list_items:
            item_frame, label, f = list_items.pop()
            item_frame.destroy()
    
    ctk.CTkButton(btn_frame, text="Add Files", command=add_pak, width=120).pack(side="left", padx=(0, 10))
    ctk.CTkButton(btn_frame, text="Remove Last Item", command=remove_pak, width=140).pack(side="left")
    
    # Conflict policy section
    policy_label = ctk.CTkLabel(
        main_frame,
        text="File Conflict Resolution:",
        font=ctk.CTkFont(size=12, weight="bold")
    )
    policy_label.pack(anchor="w", pady=(0, 10))
    
    overwrite_var = ctk.StringVar(value="overwrite" if settings.multi_pack_overwrite else "keep")
    
    ctk.CTkRadioButton(
        main_frame,
        text="Overwrite existing files (Mod edits are always highest priority)",
        variable=overwrite_var,
        value="overwrite"
    ).pack(anchor="w", pady=5)
    
    ctk.CTkRadioButton(
        main_frame,
        text="Keep existing files (do not overwrite)",
        variable=overwrite_var,
        value="keep"
    ).pack(anchor="w", pady=5)
    
    def save_settings():
        """Save settings and close dialog."""
        settings.multi_pack_files = [item[2] for item in list_items]
        settings.multi_pack_overwrite = overwrite_var.get() == "overwrite"
        settings.save()
        win.destroy()
    
    # Save button
    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.pack(fill="x", pady=(15, 0))
    
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
        command=save_settings,
        width=120,
        height=35
    ).pack(side="right")
    
    win.grab_set()

