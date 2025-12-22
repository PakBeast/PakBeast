"""File export operations."""

from pathlib import Path
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App

from core.constants import APP_NAME


def export_file_as_txt(app: 'App') -> None:
    """Export the currently open file as a TXT file."""
    if not app.current_file:
        messagebox.showwarning(
            APP_NAME,
            "No file selected.\n\n"
            "Please select a file from the file tree to export."
        )
        return
    
    # Get the content from the preview text widget
    try:
        content = app.txt.get("1.0", "end-1c")
        if not content or content.strip() == "":
            messagebox.showwarning(
                APP_NAME,
                "No content to export.\n\n"
                "The selected file appears to be empty or cannot be exported."
            )
            return
    except Exception as e:
        messagebox.showerror(
            APP_NAME,
            f"Error reading file content.\n\n"
            f"Error: {e}"
        )
        return
    
    # Determine default filename based on current file
    default_name = app.current_file.stem + ".txt"
    
    # Get export directory from settings, or use project directory as fallback
    export_dir = app.settings.last_export_dir or app.settings.last_project_dir
    
    # Show save dialog
    p = filedialog.asksaveasfilename(
        initialdir=export_dir,
        initialfile=default_name,
        defaultextension=".txt",
        filetypes=[("Text File", "*.txt"), ("All files", "*.*")]
    )
    if not p:
        return
    
    # Save the export directory to settings
    app.settings.last_export_dir = str(Path(p).parent)
    app.settings.save()
    
    # Write the content to the file
    try:
        output_path = Path(p)
        output_path.write_text(content, encoding="utf-8")
        
        if hasattr(app, '_update_status'):
            app._update_status(f"File exported: {output_path.name}", "#4CAF50")  # Green
        else:
            app.status.set(f"File exported: {output_path.name}")
        
        messagebox.showinfo(
            APP_NAME,
            f"File exported successfully.\n\n"
            f"Saved to: {output_path}\n\n"
            f"The file content has been exported as a text file."
        )
    except Exception as e:
        messagebox.showerror(
            APP_NAME,
            f"Failed to export file.\n\n"
            f"Error: {e}\n\n"
            f"The file could not be saved."
        )
