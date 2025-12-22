"""Main application class using CustomTkinter."""

from __future__ import annotations

import sys
import customtkinter as ctk
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from tkinter import messagebox

from .constants import APP_NAME, APP_DIR
from .models import ModEdit
from .settings import Settings, ensure_dir

# Import operations
from editor.operations import (
    file_tree,
    preview_handler,
    search_operations,
)
from editor.operations.pack.packer import pack_pak
import editor.operations.edits as edit_operations

# Import dialogs
from dialogs import (
    EditDialog
)


class App(ctk.CTk):
    """Main application window using CustomTkinter."""
    
    def __init__(self) -> None:
        super().__init__()
        
        # Initialize settings FIRST before using them
        self.settings = Settings()
        ensure_dir(APP_DIR)
        
        self.title(APP_NAME)
        
        # Minimum size optimized for 3-column layout:
        # Left (File Explorer ~300px) + Middle (Preview flexible) + Right (Search & Edits ~380px) + padding
        self.minsize(1300, 700)
        
        # Default window size optimized for 3-column layout with comfortable spacing
        # Width: 1600px provides ~896px for preview area (300 + 896 + 380 + 24 padding)
        # Height: 900px ensures all panels have adequate vertical space
        width = 1600
        height = 900
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configure appearance - follow OS theme
        appearance_mode = "system"
        ctk.set_appearance_mode(appearance_mode)
        ctk.set_default_color_theme("blue")  # Use default blue theme
        
        # Application state
        self.temp_root: Optional[Path] = None
        self.current_file: Optional[Path] = None
        self.current_pak_path: Optional[Path] = None
        self.search_results: List[ModEdit] = []
        self.active_edits: Dict[Tuple[str, int, int], ModEdit] = {}
        self.project_is_dirty = False
        self.path_to_id: Dict[Path, str] = {}
        self.progress_win: Optional[ctk.CTkToplevel] = None
        self._search_after_id = None
        self.filter_edit_type = ctk.StringVar(value="All Types")
        self.filter_file_path = ctk.StringVar(value="All Files")
        self.search_edits_var = ctk.StringVar()
        self._edit_search_after_id = None
        self._icon_photo = None  # Keep reference to prevent garbage collection
        self._is_searching = False  # Flag to track if search is in progress
        self._is_filtering = False  # Flag to track if filtering is in progress
        self._filter_thread = None  # Reference to background filter thread
        
        # Build UI
        from ui import ui_builder
        ui_builder.build_ui(self)
        
        # Configure text tags
        preview_handler.configure_text_tags(self)
        
        # Set application icon - try immediately and also after window is shown
        # CustomTkinter may set its default icon, so we need to override it
        self._set_app_icon()
        self.after(100, self._set_app_icon)
        self.after_idle(self._set_app_icon)
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _set_app_icon(self) -> None:
        """Set the application window icon."""
        try:
            from ui.utils import _load_icon_photo

            photo_info = _load_icon_photo()
            photo = None
            icon_path = None
            if photo_info:
                photo, icon_path = photo_info

            tk_window = self.tk if hasattr(self, "tk") else self

            if photo is not None:
                self._icon_photo = photo
                tk_window.iconphoto(True, self._icon_photo)
                try:
                    import tkinter as tk

                    if tk._default_root:
                        tk._default_root.iconphoto(True, self._icon_photo)
                except Exception:
                    pass
                return

            if icon_path:
                try:
                    tk_window.iconbitmap(str(icon_path))
                except Exception:
                    pass
        except Exception:
            pass
    
    # File Operations
    def _load_pak(self) -> None:
        from editor.operations.files.loading import load_pak
        load_pak(self)
    
    def _populate_tree(self, root: Path) -> None:
        file_tree.populate_tree(self, root)
    
    def _finish_loading(self, pak_name: str):
        from editor.operations.files.loading import finish_loading
        finish_loading(self, pak_name)
    
    def _loading_failed(self, error: Exception):
        from editor.operations.files.loading import loading_failed
        loading_failed(self, error)
    
    def _cleanup_temp(self) -> None:
        from editor.operations.files.loading import cleanup_temp
        cleanup_temp(self)
    
    def _save_project(self) -> None:
        from editor.operations.files.saving import save_project
        save_project(self)
    
    def _load_project(self) -> None:
        from editor.operations.files.saving import load_project
        load_project(self)
    
    def _export_file_as_txt(self) -> None:
        from editor.operations.files.export import export_file_as_txt
        export_file_as_txt(self)
    
    # File Tree Operations
    def _on_file_search_change(self, *args):
        file_tree.on_file_search_change(self, *args)
    
    def _filter_file_tree(self):
        file_tree.filter_file_tree(self)
    
    def _on_tree_select(self, _evt=None) -> None:
        file_tree.on_tree_select(self, _evt)
    
    def _on_tree_select_path(self, path: Path):
        preview_handler.on_tree_select_path(self, path)
    
    # Preview Operations
    def _on_preview_double_click(self, _evt=None) -> None:
        edit_operations.on_preview_double_click(self, _evt)
    
    def _on_preview_right_click(self, event):
        from editor.operations.preview_edit_operations import on_preview_right_click
        on_preview_right_click(self, event)
    
    def _show_edit_in_preview(self, edit: ModEdit):
        preview_handler.show_edit_in_preview(self, edit)
    
    def _apply_syntax_highlighting(self):
        preview_handler.apply_syntax_highlighting(self)
    
    def _find_context_name(self, target_line: int) -> Optional[str]:
        return preview_handler.find_context_name(self, target_line)
    
    # Search Operations
    def _find_params(self) -> None:
        search_operations.find_params(self)
    
    def _on_result_select(self, _evt=None) -> None:
        search_operations.on_result_select(self, _evt)
    
    def _on_add_from_result(self, _evt=None) -> None:
        search_operations.on_add_from_result(self, _evt)
    
    # Edit Operations
    def _get_filtered_and_sorted_edits(self):
        return edit_operations.get_filtered_and_sorted_edits(self)
    
    def _refresh_edits_list(self) -> None:
        edit_operations.refresh_edits_list(self)
    
    def _selected_edit(self) -> Optional[ModEdit]:
        return edit_operations.selected_edit(self)
    
    def _on_edit_select(self, _evt=None):
        edit_operations.on_edit_select(self, _evt)
    
    def _toggle_selected_edit(self):
        edit_operations.toggle_selected_edit(self)
    
    def _delete_selected_edit(self):
        edit_operations.delete_selected_edit(self)
    
    def _clear_edits(self):
        edit_operations.clear_edits(self)
    
    def _enable_all_filtered(self):
        edit_operations.enable_all_filtered(self)
    
    def _disable_all_filtered(self):
        edit_operations.disable_all_filtered(self)
    
    def _edits_context(self, event) -> None:
        edit_operations.edits_context(self, event)
    
    def _edit_selected_value(self) -> None:
        edit_operations.edit_selected_value(self)
    
    def _edit_inserted_text(self):
        edit_operations.edit_inserted_text(self)
    
    # Packing Operations
    def _pack_pak(self) -> None:
        pack_pak(self)
    
    # Settings and Dialogs
    
    def _show_progress(self, text: str):
        """Show progress message with blue dot (processing)."""
        if hasattr(self, '_update_status'):
            self._update_status(text, "#2196F3")  # Blue for processing
        else:
            self.status.set(text)
    
    def _hide_progress(self):
        """Hide progress message and set to ready."""
        if hasattr(self, '_update_status'):
            self._update_status("Ready", "#4CAF50")  # Green for ready
        else:
            self.status.set("Ready")
    
    def _open_color_settings(self) -> None:
        """Switch to Appearance tab."""
        if hasattr(self, 'main_tabs'):
            self.main_tabs.set("Appearance")
    
    def _on_filter_change_debounced(self, *args):
        """Debounced filter change handler."""
        if self._edit_search_after_id:
            self.after_cancel(self._edit_search_after_id)
        self._edit_search_after_id = self.after(300, self._on_filter_change)
    
    def _on_filter_change(self, _evt=None) -> None:
        """Handle filter change - uses background threading for large datasets."""
        from editor.operations.edits.filtering import filter_edits_in_background
        filter_edits_in_background(self)
    
    def _on_close(self) -> None:
        """Handle window close."""
        if self.project_is_dirty and not messagebox.askyesno(
            "Exit Application",
            "You have unsaved changes that will be lost.\n\n"
            "Are you sure you want to exit?"
        ):
            return
        self._cleanup_temp()
        self.destroy()


def main() -> None:
    """Main entry point."""
    # This check is necessary for multiprocessing to work correctly when frozen with PyInstaller on Windows.
    if sys.platform.startswith('win'):
        import multiprocessing
        multiprocessing.freeze_support()
    
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()

