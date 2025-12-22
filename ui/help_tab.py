"""Help tab building functions."""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App


def build_help_tab(app: 'App', parent):
    """Build the help/about tab."""
    help_container = ctk.CTkFrame(parent, fg_color="transparent")
    help_container.pack(fill="both", expand=True, padx=12, pady=12)
    
    # Create scrollable frame
    scrollable = ctk.CTkScrollableFrame(help_container)
    scrollable.pack(fill="both", expand=True, padx=0, pady=(0, 12))
    
    from core.constants import APP_NAME
    
    # Header Section - enhanced styling
    header_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
    header_frame.pack(fill="x", padx=14, pady=(14, 20))
    
    title = ctk.CTkLabel(
        header_frame,
        text=APP_NAME,
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=("gray10", "gray90"),
    )
    title.pack(anchor="w")
    
    # Overview Section - enhanced styling
    overview_section = ctk.CTkFrame(
        scrollable,
        fg_color=("gray98", "gray18"),
        border_width=1,
        border_color=("gray80", "gray25"),
        corner_radius=10
    )
    overview_section.pack(fill="x", padx=14, pady=(0, 20))
    
    overview_title = ctk.CTkLabel(
        overview_section,
        text="Overview",
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color=("gray10", "gray90"),
    )
    overview_title.pack(anchor="w", padx=14, pady=(14, 10))
    
    overview_text = ctk.CTkLabel(
        overview_section,
        text="Extract, search, and edit Dying Light: The Beast game files from .pak archives.\n"
             "Modify parameters, properties, and code blocks. Build modified .pak files for in-game use.",
        font=ctk.CTkFont(size=11),
        justify="left",
        anchor="w",
        text_color=("gray30", "gray80")
    )
    overview_text.pack(anchor="w", padx=14, pady=(0, 14))
    
    # Code Elements Section - enhanced styling
    elements_section = ctk.CTkFrame(
        scrollable,
        fg_color=("gray98", "gray18"),
        border_width=1,
        border_color=("gray80", "gray25"),
        corner_radius=10
    )
    elements_section.pack(fill="x", padx=14, pady=(0, 20))
    
    elements_title = ctk.CTkLabel(
        elements_section,
        text="Code Elements",
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color=("gray10", "gray90"),
    )
    elements_title.pack(anchor="w", padx=14, pady=(14, 12))
    
    # Help content - horizontal layout
    help_sections = [
        {
            "title": "Parameters",
            "example": 'Param("MaxAmmo", 30);',
            "description": "Gameplay configuration values.",
            "instructions": "Double-click to edit."
        },
        {
            "title": "Properties",
            "example": 'GameName("Dying Light: The Beast");',
            "description": "Function calls with values.",
            "instructions": "Double-click to edit."
        },
        {
            "title": "Code Blocks",
            "example": 'AttackPreset("name") { ... }',
            "description": "Multi-line entity definitions.",
            "instructions": "Double-click header to delete."
        }
    ]
    
    # Container for horizontal layout
    elements_container = ctk.CTkFrame(elements_section, fg_color="transparent")
    elements_container.pack(fill="x", padx=16, pady=(0, 16))
    
    for idx, section in enumerate(help_sections):
        section_frame = ctk.CTkFrame(elements_container, fg_color="transparent")
        section_frame.pack(side="left", fill="both", expand=True, padx=(0, 12) if idx < len(help_sections) - 1 else (0, 0))
        
        section_title_label = ctk.CTkLabel(
            section_frame,
            text=section["title"],
            font=ctk.CTkFont(size=13, weight="bold")
        )
        section_title_label.pack(anchor="w", pady=(0, 6))
        
        # Example code
        example_frame = ctk.CTkFrame(
            section_frame,
            fg_color=("gray90", "gray15"),
            corner_radius=4
        )
        example_frame.pack(fill="x", pady=(0, 6))
        
        example_label = ctk.CTkLabel(
            example_frame,
            text=section["example"],
            font=ctk.CTkFont(family="Consolas", size=11),
            anchor="w"
        )
        example_label.pack(anchor="w", padx=10, pady=6)
        
        # Description and instructions combined
        desc_label = ctk.CTkLabel(
            section_frame,
            text=f"{section['description']} {section['instructions']}",
            font=ctk.CTkFont(size=11),
            justify="left",
            anchor="w",
            text_color=("gray30", "gray80")
        )
        desc_label.pack(anchor="w", pady=(0, 8))
    
    # Usage Tips Section - enhanced styling
    tips_section = ctk.CTkFrame(
        scrollable,
        fg_color=("gray98", "gray18"),
        border_width=1,
        border_color=("gray80", "gray25"),
        corner_radius=10
    )
    tips_section.pack(fill="x", padx=14, pady=(0, 20))
    
    tips_title = ctk.CTkLabel(
        tips_section,
        text="Tips",
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color=("gray10", "gray90"),
    )
    tips_title.pack(anchor="w", padx=14, pady=(14, 12))
    
    tips = [
        "Search is case-insensitive across .scr, .ini, .loot, .gui, .cfg, .json, .txt files",
        "Single-click search results to preview, double-click to add edits",
        "Export files as TXT for comparison or external editing",
        "Save projects (.pbm) to preserve your modifications",
        "Build mod to compile edited files into a new .pak archive"
    ]
    
    # Container for tips layout (similar to Code Elements structure)
    tips_container = ctk.CTkFrame(tips_section, fg_color="transparent")
    tips_container.pack(fill="x", padx=16, pady=(0, 16))
    
    for tip in tips:
        tip_frame = ctk.CTkFrame(tips_container, fg_color="transparent")
        tip_frame.pack(fill="x", pady=(0, 8))
        
        tip_label = ctk.CTkLabel(
            tip_frame,
            text=f"• {tip}",
            font=ctk.CTkFont(size=11),
            anchor="w",
            justify="left",
            text_color=("gray30", "gray80")
        )
        tip_label.pack(anchor="w")

