"""Changes viewer UI component for displaying parameter changes."""

import customtkinter as ctk

from ..operations.models import FileDiff


def populate_changes_viewer(params_list: ctk.CTkScrollableFrame, diff: FileDiff) -> None:
    """Populate the changes viewer with parameter changes."""
    for child in params_list.winfo_children():
        child.destroy()
    
    if diff.param_changes:
        # Compact summary header
        summary_frame = ctk.CTkFrame(
            params_list, 
            fg_color=("gray93", "gray22"), 
            corner_radius=5,
            border_width=1,
            border_color=("gray80", "gray30")
        )
        summary_frame.pack(fill="x", padx=2, pady=(0, 8))
        
        summary_label = ctk.CTkLabel(
            summary_frame,
            text=f"✨ {len(diff.param_changes)} Change{'s' if len(diff.param_changes) != 1 else ''}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray10", "gray90"),
        )
        summary_label.pack(padx=10, pady=6)
        
        # Display each change in a more compact format
        for idx, (name, old, new) in enumerate(diff.param_changes, 1):
            # Compact change container
            change_container = ctk.CTkFrame(
                params_list, 
                fg_color=("gray96", "gray17"), 
                corner_radius=5,
                border_width=1,
                border_color=("gray85", "gray25")
            )
            change_container.pack(fill="x", padx=2, pady=3)
            
            # Top row: Parameter name and badge
            header_row = ctk.CTkFrame(change_container, fg_color="transparent")
            header_row.pack(fill="x", padx=8, pady=(6, 4))
            
            # Compact badge
            badge = ctk.CTkLabel(
                header_row,
                text=f"#{idx}",
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color="#2196F3",
                width=24,
            )
            badge.pack(side="left", padx=(0, 6))
            
            # Parameter name
            name_label = ctk.CTkLabel(
                header_row,
                text=name,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("black", "white"),
                anchor="w",
            )
            name_label.pack(side="left", fill="x", expand=True)
            
            # Compact side-by-side comparison (horizontal layout)
            comparison_row = ctk.CTkFrame(change_container, fg_color="transparent")
            comparison_row.pack(fill="x", padx=8, pady=(0, 6))
            
            # Original value (compact)
            old_str = str(old) if old else "(empty)"
            if len(old_str) > 80:
                old_display = old_str[:77] + "..."
            else:
                old_display = old_str
            
            old_frame = ctk.CTkFrame(
                comparison_row,
                fg_color=("gray94", "gray20"),
                corner_radius=4,
                border_width=1,
                border_color="#e57373"
            )
            old_frame.pack(side="left", fill="both", expand=True, padx=(0, 4))
            
            old_label = ctk.CTkLabel(
                old_frame,
                text=f"➖ {old_display}",
                font=ctk.CTkFont(size=10, family="Consolas"),
                text_color="#e57373",
                anchor="w",
                wraplength=200,
            )
            old_label.pack(fill="x", padx=6, pady=4)
            if len(old_str) > 80:
                old_label._full_value = old_str
            
            # Arrow
            arrow = ctk.CTkLabel(
                comparison_row,
                text="→",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#FFA726",
                width=20,
            )
            arrow.pack(side="left", padx=2)
            
            # New value (compact)
            new_str = str(new) if new else "(empty)"
            if len(new_str) > 80:
                new_display = new_str[:77] + "..."
            else:
                new_display = new_str
            
            new_frame = ctk.CTkFrame(
                comparison_row,
                fg_color=("gray94", "gray20"),
                corner_radius=4,
                border_width=1,
                border_color="#81c784"
            )
            new_frame.pack(side="left", fill="both", expand=True, padx=(4, 0))
            
            new_label = ctk.CTkLabel(
                new_frame,
                text=f"➕ {new_display}",
                font=ctk.CTkFont(size=10, family="Consolas"),
                text_color="#81c784",
                anchor="w",
                wraplength=200,
            )
            new_label.pack(fill="x", padx=6, pady=4)
            if len(new_str) > 80:
                new_label._full_value = new_str
    else:
        # Compact "no changes" message
        no_changes_frame = ctk.CTkFrame(
            params_list, 
            fg_color=("gray95", "gray20"), 
            corner_radius=5,
            border_width=1,
            border_color=("gray85", "gray30")
        )
        no_changes_frame.pack(fill="x", padx=2, pady=10)
        
        no_changes_label = ctk.CTkLabel(
            no_changes_frame,
            text="✓ No changes detected",
            text_color="#90A4AE",
            font=ctk.CTkFont(size=11),
        )
        no_changes_label.pack(padx=15, pady=12)
