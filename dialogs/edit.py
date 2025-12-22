"""Edit dialog using CustomTkinter."""

import customtkinter as ctk
from typing import Optional, Tuple
from ui.utils import set_window_icon


class EditDialog:
    """Custom dialog for editing a property's value and its description."""
    
    def __init__(self, parent, title, param_name, initial_desc, initial_val):
        self.param_name = param_name
        self.initial_desc = initial_desc
        self.initial_val = initial_val
        self.result: Optional[Tuple[str, str]] = None
        
        # Create dialog window
        self.win = ctk.CTkToplevel(parent)
        self.win.title(title)
        self.win.transient(parent)
        self.win.resizable(True, True)
        self.win.minsize(520, 320)
        
        # Center window relative to parent (use explicit dimensions)
        self.win.update_idletasks()
        
        # Set icon after window is created and updated
        set_window_icon(self.win)
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        dialog_width = 520
        dialog_height = 320
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        self.win.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Main frame with compact spacing
        main_frame = ctk.CTkFrame(self.win, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Header section - compact
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 12))
        
        header_title = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        header_title.pack(anchor="w")
        
        property_name_label = ctk.CTkLabel(
            header_frame,
            text=f"Property: {self.param_name}",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray70")
        )
        property_name_label.pack(anchor="w", pady=(2, 0))
        
        # Description field section - compact
        desc_label = ctk.CTkLabel(
            main_frame,
            text="Description:",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        desc_label.pack(anchor="w", pady=(0, 4))
        
        self.desc_entry = ctk.CTkEntry(
            main_frame,
            height=32,
            font=ctk.CTkFont(size=11),
            corner_radius=5
        )
        self.desc_entry.pack(fill="x", pady=(0, 12))
        self.desc_entry.insert(0, self.initial_desc)

        # Value field section - compact
        val_label = ctk.CTkLabel(
            main_frame,
            text="Value:",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        val_label.pack(anchor="w", pady=(0, 4))
        
        self.val_entry = ctk.CTkTextbox(
            main_frame,
            font=("Consolas", 10),
            corner_radius=5,
            height=100
        )
        self.val_entry.pack(fill="both", expand=True, pady=(0, 12))
        self.val_entry.insert("1.0", self.initial_val)
        
        # Buttons - compact
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._cancel,
            width=100,
            height=32,
            font=ctk.CTkFont(size=11),
            corner_radius=5
        )
        cancel_btn.pack(side="right", padx=(8, 0))
        
        apply_btn = ctk.CTkButton(
            button_frame,
            text="Apply",
            command=self._apply,
            width=100,
            height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=5
        )
        apply_btn.pack(side="right")
        
        # Bind Enter key to apply
        def on_enter_key(event):
            """Handle Enter key press to apply changes."""
            self._apply()
            return "break"
        
        # For textbox, Enter applies (use Shift+Enter for new line if needed)
        self.val_entry.bind("<Return>", on_enter_key)
        # For entry field, Enter applies directly
        self.desc_entry.bind("<Return>", on_enter_key)
        
        # Focus on value entry and select all text for quick editing
        self.win.after(100, lambda: self._focus_and_select_value())
        
        # Make dialog modal
        self.win.grab_set()
        self.win.wait_window()
    
    def _focus_and_select_value(self):
        """Focus the value entry and select all text for quick editing."""
        self.val_entry.focus_set()
        # Select all text in the textbox
        try:
            # CTkTextbox has a _textbox attribute that is the underlying tkinter Text widget
            if hasattr(self.val_entry, '_textbox'):
                text_widget = self.val_entry._textbox
                # Select all text
                text_widget.tag_add("sel", "1.0", "end")
                text_widget.mark_set("insert", "end")
        except Exception:
            # If selection fails, just ensure focus is set
            pass
    
    def _apply(self):
        """Apply changes and close dialog."""
        val = self.val_entry.get("1.0", "end-1c").strip()
        self.result = (self.desc_entry.get(), val)
        self.win.destroy()
    
    def _cancel(self):
        """Cancel and close dialog."""
        self.result = None
        self.win.destroy()

