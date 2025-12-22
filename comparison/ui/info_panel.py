"""Info panel UI component for comparison results."""

from pathlib import Path
import customtkinter as ctk

from ..operations.models import FileDiff


def populate_info_panel(
    info_content: ctk.CTkScrollableFrame,
    diff: FileDiff,
    original_path: Path,
    modded_path: Path,
) -> None:
    """Populate the info panel with comparison statistics and metadata."""
    for child in info_content.winfo_children():
        child.destroy()
    
    if not diff:
        empty_label = ctk.CTkLabel(
            info_content,
            text="Run a comparison to see details here",
            text_color=("gray50", "gray60"),
            font=ctk.CTkFont(size=11),
        )
        empty_label.pack(padx=10, pady=20)
        return
    
    # File information section
    file_info_frame = ctk.CTkFrame(
        info_content,
        fg_color=("gray95", "gray20"),
        corner_radius=6,
        border_width=1,
        border_color=("gray85", "gray30"),
    )
    file_info_frame.pack(fill="x", padx=5, pady=(0, 10))
    
    file_info_title = ctk.CTkLabel(
        file_info_frame,
        text="📄 Files",
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color=("gray10", "gray90"),
    )
    file_info_title.pack(anchor="w", padx=10, pady=(8, 4))
    
    # Original file info
    orig_info = ctk.CTkLabel(
        file_info_frame,
        text=f"Original: {original_path.name}",
        font=ctk.CTkFont(size=10),
        text_color=("#e57373", "#e57373"),
        anchor="w",
    )
    orig_info.pack(fill="x", padx=10, pady=2)
    
    # Modded file info
    mod_info = ctk.CTkLabel(
        file_info_frame,
        text=f"Modified: {modded_path.name}",
        font=ctk.CTkFont(size=10),
        text_color=("#81c784", "#81c784"),
        anchor="w",
    )
    mod_info.pack(fill="x", padx=10, pady=(2, 8))
    
    # Statistics section
    stats_frame = ctk.CTkFrame(
        info_content,
        fg_color=("gray95", "gray20"),
        corner_radius=6,
        border_width=1,
        border_color=("gray85", "gray30"),
    )
    stats_frame.pack(fill="x", padx=5, pady=(0, 10))
    
    stats_title = ctk.CTkLabel(
        stats_frame,
        text="📊 Statistics",
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color=("gray10", "gray90"),
    )
    stats_title.pack(anchor="w", padx=10, pady=(8, 4))
    
    # Parameter changes count
    param_count = len(diff.param_changes) if diff.param_changes else 0
    param_label = ctk.CTkLabel(
        stats_frame,
        text=f"Parameter Changes: {param_count}",
        font=ctk.CTkFont(size=10),
        text_color=("gray10", "gray90"),
        anchor="w",
    )
    param_label.pack(fill="x", padx=10, pady=2)
    
    # Changed lines count
    changed_lines = diff.changed_lines if diff.changed_lines else []
    lines_label = ctk.CTkLabel(
        stats_frame,
        text=f"Changed Lines: {len(changed_lines)}",
        font=ctk.CTkFont(size=10),
        text_color=("gray10", "gray90"),
        anchor="w",
    )
    lines_label.pack(fill="x", padx=10, pady=(2, 8))
    
    # File sizes (if available)
    try:
        orig_size = original_path.stat().st_size
        mod_size = modded_path.stat().st_size
        size_info = ctk.CTkLabel(
            stats_frame,
            text=f"Original Size: {orig_size:,} bytes\nModified Size: {mod_size:,} bytes",
            font=ctk.CTkFont(size=9),
            text_color=("gray50", "gray60"),
            anchor="w",
            justify="left",
        )
        size_info.pack(fill="x", padx=10, pady=(0, 8))
    except:
        pass
