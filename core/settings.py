"""Settings management for the mod tool."""

import json
from pathlib import Path
from typing import Dict, List

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
        self.dark_mode: bool = bool(data.get("dark_mode", False))
        self.multi_pack_files: List[str] = data.get("multi_pack_files", [])
        self.multi_pack_overwrite: bool = data.get("multi_pack_overwrite", True)
        
        colors = data.get("colors", {})
        self.colors = {
            "light": {
                # Bright blue for parameters - clear and professional for code editing
                "param": colors.get("light", {}).get("param", "#0078d4"),
                # Teal/green for properties - distinct and easy to read
                "prop": colors.get("light", {}).get("prop", "#00a651"),
                # Deep purple for block headers - stands out for structure
                "block_header": colors.get("light", {}).get("block_header", "#6b46c1"),
            },
            "dark": {
                # Bright cyan-blue for parameters - excellent for dark code editors
                "param": colors.get("dark", {}).get("param", "#4fc3f7"),
                # Green/cyan for properties - vibrant and readable in dark mode
                "prop": colors.get("dark", {}).get("prop", "#26c6da"),
                # Purple/magenta for block headers - prominent in dark themes
                "block_header": colors.get("dark", {}).get("block_header", "#ba68c8"),
            }
        }

    def save(self) -> None:
        """Save settings to disk."""
        write_json(CONFIG_PATH, {
            "last_pak_dir": self.last_pak_dir,
            "last_project_dir": self.last_project_dir,
            "dark_mode": self.dark_mode,
            "multi_pack_files": self.multi_pack_files,
            "multi_pack_overwrite": self.multi_pack_overwrite,
            "colors": self.colors,
        })

