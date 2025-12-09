"""Preview panel operations for displaying and highlighting file content."""

from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App
    from core.models import ModEdit

from core.constants import PARAM_RE, PROP_RE, BLOCK_HEADER_RE
from logic.scanner import _find_block_context_name


def configure_text_tags(app: 'App'):
    """Configure text tags for syntax highlighting using CustomTkinter theme colors."""
    import customtkinter as ctk
    
    # Get current appearance mode
    current_mode = ctk.get_appearance_mode()
    if current_mode == "Dark":
        is_dark = True
    elif current_mode == "Light":
        is_dark = False
    else:  # System mode - try to detect
        try:
            import tkinter as tk
            test_root = tk.Tk()
            test_root.withdraw()
            bg = test_root.cget("bg")
            test_root.destroy()
            # Simple heuristic: check if background is dark
            dark_bgs = ["#212121", "#1e1e1e", "#2b2b2b", "#1f1f1f"]
            is_dark = any(bg.lower() == dbg.lower() for dbg in dark_bgs) or (len(bg) == 7 and bg[0] == "#" and int(bg[1:3], 16) < 0x40)
        except:
            is_dark = False
    
    # Use user-defined colors from settings
    colors = app.settings.colors
    
    # Configure syntax highlighting tags
    app.txt.tag_configure("param", foreground=colors["param"])
    app.txt.tag_configure("prop", foreground=colors["prop"])
    app.txt.tag_configure("block_header", foreground=colors["block_header"], font=("Consolas", 11, "bold"))
    
    # Use theme-appropriate background/foreground
    if is_dark:
        bg = "#1e1e1e"
        fg = "#d4d4d4"
    else:
        bg = "#FFFFFF"
        fg = "#000000"
    
    app.txt.config(bg=bg, fg=fg, insertbackground=fg)


def apply_syntax_highlighting(app: 'App'):
    """Apply syntax highlighting to the preview text."""
    app.txt.tag_remove("param", "1.0", "end")
    app.txt.tag_remove("prop", "1.0", "end")
    app.txt.tag_remove("block_header", "1.0", "end")
    content = app.txt.get("1.0", "end-1c")
    for i, line in enumerate(content.splitlines()):
        line_num_str = str(i + 1)
        for m in PARAM_RE.finditer(line):
            app.txt.tag_add("param", f"{line_num_str}.{m.start()}", f"{line_num_str}.{m.end()}")
        for m in PROP_RE.finditer(line):
            app.txt.tag_add("prop", f"{line_num_str}.{m.start()}", f"{line_num_str}.{m.end()}")
        for m in BLOCK_HEADER_RE.finditer(line):
            app.txt.tag_add("block_header", f"{line_num_str}.{m.start()}", f"{line_num_str}.{m.end()}")
    
    # Update line numbers after highlighting
    if hasattr(app, '_update_line_numbers'):
        app._update_line_numbers()


def on_tree_select_path(app: 'App', path: Path):
    """Handle file selection from tree."""
    app.current_file = path
    if app.temp_root:
        relative_path = path.relative_to(app.temp_root)
        from ui.utils import shorten_path
        label = shorten_path(relative_path, max_length=60)
    else:
        label = path.name
    app.preview_label.configure(text=f"File Preview: {label}")
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        content = f"<Error reading file: {e}>"
    
    app.txt.config(state="normal")
    app.txt.delete("1.0", "end")
    app.txt.insert("1.0", content)
    app.txt.tag_remove("highlight", "1.0", "end")
    app.txt.tag_remove("hover", "1.0", "end")
    apply_syntax_highlighting(app)
    app.txt.config(state="disabled")
    
    # Update line numbers
    if hasattr(app, '_update_line_numbers'):
        app._update_line_numbers()


def find_context_name(app: 'App', target_line: int) -> Optional[str]:
    """Find the context name for a given line."""
    app.txt.config(state="normal")
    lines = app.txt.get("1.0", "end-1c").splitlines()
    app.txt.config(state="disabled")
    return _find_block_context_name(target_line, lines)


def show_edit_in_preview(app: 'App', edit: ModEdit):
    """Show and highlight an edit in the preview panel."""
    if not edit:
        return
    file_path = Path(edit.file_path)
    
    def highlight():
        app.txt.config(state="normal")
        app.txt.tag_remove("highlight", "1.0", "end")
        start, end = f"{edit.line_number + 1}.0", f"{edit.end_line_number + 1}.end"
        app.txt.see(start)
        app.txt.tag_add("highlight", start, end)
        app.txt.config(state="disabled")

    if app.current_file != file_path:
        item_id = app.path_to_id.get(file_path)
        if item_id and app.tree.exists(item_id):
            app.tree.selection_set(item_id)
            app.tree.focus(item_id)
            app.tree.see(item_id)
            app.after(50, highlight)
        else:
            on_tree_select_path(app, file_path)
            app.after(50, highlight)
    else:
        highlight()

