"""Help tab building functions."""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App


def build_help_tab(app: 'App', parent):
    """Build the help/about tab."""
    help_container = ctk.CTkFrame(parent, fg_color="transparent")
    help_container.pack(fill="both", expand=True, padx=16, pady=(12, 16))
    
    # Create scrollable frame
    scrollable = ctk.CTkScrollableFrame(help_container)
    scrollable.pack(fill="both", expand=True, padx=0, pady=(0, 16))
    
    from core.constants import APP_NAME
    
    # Header Section
    header_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
    header_frame.pack(fill="x", padx=12, pady=(12, 25))
    
    title = ctk.CTkLabel(
        header_frame,
        text=APP_NAME,
        font=ctk.CTkFont(size=18, weight="bold")
    )
    title.pack(anchor="w")
    
    # Overview Section
    overview_section = ctk.CTkFrame(
        scrollable,
        fg_color=("gray95", "gray20"),
        border_width=1,
        border_color=("gray80", "gray30"),
        corner_radius=8
    )
    overview_section.pack(fill="x", padx=12, pady=(0, 20))
    
    overview_title = ctk.CTkLabel(
        overview_section,
        text="Overview",
        font=ctk.CTkFont(size=14, weight="bold")
    )
    overview_title.pack(anchor="w", padx=16, pady=(16, 10))
    
    overview_text = ctk.CTkLabel(
        overview_section,
        text="Modify .scr script files by searching for parameters, properties, and code blocks.\n"
             "Create modifications, save projects, and compile .pak mod packages for use in-game.",
        font=ctk.CTkFont(size=11),
        justify="left",
        anchor="w",
        text_color=("white", "white")
    )
    overview_text.pack(anchor="w", padx=16, pady=(0, 16))
    
    # Code Elements Section
    elements_section = ctk.CTkFrame(
        scrollable,
        fg_color=("gray95", "gray20"),
        border_width=1,
        border_color=("gray80", "gray30"),
        corner_radius=8
    )
    elements_section.pack(fill="x", padx=12, pady=(0, 20))
    
    elements_title = ctk.CTkLabel(
        elements_section,
        text="Code Elements",
        font=ctk.CTkFont(size=14, weight="bold")
    )
    elements_title.pack(anchor="w", padx=16, pady=(16, 12))
    
    # Help content - horizontal layout
    help_sections = [
        {
            "title": "Parameters",
            "example": 'Param("MaxAmmo", 30);',
            "description": "Named value assignments for gameplay values.",
            "instructions": "Double-click in preview to modify."
        },
        {
            "title": "Properties",
            "example": 'Price(1500);',
            "description": "Value assignments within block definitions.",
            "instructions": "Double-click to edit."
        },
        {
            "title": "Code Blocks",
            "example": 'AttackPreset("biter_grab") { ... }',
            "description": "Multi-line structures defining game entities.",
            "instructions": "Double-click header to delete block."
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
            text_color=("white", "white")
        )
        desc_label.pack(anchor="w", pady=(0, 8))
    
    # Usage Tips Section
    tips_section = ctk.CTkFrame(
        scrollable,
        fg_color=("gray95", "gray20"),
        border_width=1,
        border_color=("gray80", "gray30"),
        corner_radius=8
    )
    tips_section.pack(fill="x", padx=12, pady=(0, 20))
    
    tips_title = ctk.CTkLabel(
        tips_section,
        text="Tips",
        font=ctk.CTkFont(size=14, weight="bold")
    )
    tips_title.pack(anchor="w", padx=16, pady=(16, 12))
    
    tips = [
        "Use Parameter Search to find values across .scr files",
        "Single-click results to preview, double-click to add modifications",
        "Save projects frequently",
        "Build mod to create .pak file"
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
            text_color=("white", "white")
        )
        tip_label.pack(anchor="w")

