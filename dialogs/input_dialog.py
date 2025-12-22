"""Simple input dialog using CustomTkinter."""

import customtkinter as ctk
from typing import Optional
from ui.utils import set_window_icon


class InputDialog:
    """Custom dialog for simple text input."""
    
    def __init__(self, parent, title: str, prompt: str, initialvalue: str = ""):
        self.result: Optional[str] = None
        self.win = ctk.CTkToplevel(parent)
        self.win.title(title)
        self.win.transient(parent)
        self.win.resizable(False, False)
        self.win.minsize(400, 140)
        
        # Center window relative to parent
        self.win.update_idletasks()
        
        # Set icon after window is created and updated
        set_window_icon(self.win)
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        dialog_width = 400
        dialog_height = 140
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        self.win.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Main frame - compact
        main_frame = ctk.CTkFrame(self.win, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Prompt label - compact
        prompt_label = ctk.CTkLabel(
            main_frame,
            text=prompt,
            font=ctk.CTkFont(size=11),
            anchor="w",
            justify="left"
        )
        prompt_label.pack(anchor="w", pady=(0, 8))
        
        # Input entry - compact
        self.entry = ctk.CTkEntry(
            main_frame,
            height=32,
            font=ctk.CTkFont(size=11),
            corner_radius=5
        )
        self.entry.pack(fill="x", pady=(0, 12))
        if initialvalue:
            self.entry.insert(0, initialvalue)
            self.entry.select_range(0, "end")
        
        # Buttons frame - compact
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._cancel,
            width=90,
            height=30,
            font=ctk.CTkFont(size=11),
            corner_radius=5
        ).pack(side="right", padx=(8, 0))
        
        ctk.CTkButton(
            button_frame,
            text="OK",
            command=self._apply,
            width=90,
            height=30,
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=5
        ).pack(side="right")
        
        # Focus on entry and bind Enter key
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda e: self._apply())
        self.entry.bind("<Escape>", lambda e: self._cancel())
        
        # Make dialog modal
        self.win.grab_set()
        self.win.wait_window()
    
    def _apply(self):
        """Apply changes and close dialog."""
        self.result = self.entry.get().strip()
        self.win.destroy()
    
    def _cancel(self):
        """Cancel and close dialog."""
        self.result = None
        self.win.destroy()

