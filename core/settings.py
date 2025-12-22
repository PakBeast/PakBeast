"""Settings management for the mod tool."""

import json
from pathlib import Path
from typing import List

from core.constants import CONFIG_PATH


def ensure_dir(p: Path) -> None:
    """Ensure a directory exists."""
    p.mkdir(parents=True, exist_ok=True)


def read_json(p: Path, default):
    """Read JSON file, return default if it doesn't exist or is invalid."""
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(p: Path, data) -> None:
    """Write JSON file atomically."""
    ensure_dir(p.parent)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(p)


class Settings:
    """Application settings manager."""
    
    def __init__(self) -> None:
        data = read_json(CONFIG_PATH, {})
        home_dir = str(Path.home())
        self.last_pak_dir: str = data.get("last_pak_dir", home_dir)
        self.last_project_dir: str = data.get("last_project_dir", home_dir)
        self.last_export_dir: str = data.get("last_export_dir", home_dir)
        
        default_colors = {
            "param": "#569cd6",      # Bright blue - excellent for parameters/functions
            "prop": "#4ec9b0",       # Cyan - distinct for properties/attributes
            "block_header": "#c586c0", # Purple - stands out for block headers/sections
            "string": "#ce9178",     # Warm orange - perfect for string literals
            "number": "#b5cea8",     # Light green - clear for numeric values
            "comment": "#6a9955",    # Muted green - traditional comment color
        }
        default_theme = {
            "background": "#1e1e1e",
            "foreground": "#d4d4d4",
            "edited_line": "#2a3a3a",
        }
        colors = data.get("colors", {})
        if isinstance(colors, dict) and ("dark" in colors or "light" in colors):
            legacy = colors.get("dark") or colors.get("light") or {}
            colors = {**default_colors, **legacy}
        self.colors = {
            "param": colors.get("param", default_colors["param"]),
            "prop": colors.get("prop", default_colors["prop"]),
            "block_header": colors.get("block_header", default_colors["block_header"]),
            "string": colors.get("string", default_colors["string"]),
            "number": colors.get("number", default_colors["number"]),
            "comment": colors.get("comment", default_colors["comment"]),
        }
        theme = data.get("theme", {})
        self.theme = {
            "background": theme.get("background", default_theme["background"]),
            "foreground": theme.get("foreground", default_theme["foreground"]),
            "edited_line": theme.get("edited_line", default_theme["edited_line"]),
        }

    def save(self) -> None:
        """Save settings to disk."""
        write_json(CONFIG_PATH, {
            "last_pak_dir": self.last_pak_dir,
            "last_project_dir": self.last_project_dir,
            "last_export_dir": self.last_export_dir,
            "colors": self.colors,
            "theme": self.theme,
        })

