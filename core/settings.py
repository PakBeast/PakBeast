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
        self.multi_pack_files: List[str] = data.get("multi_pack_files", [])
        self.multi_pack_overwrite: bool = data.get("multi_pack_overwrite", True)
        
        default_colors = {
            "param": "#4fc3f7",
            "prop": "#26c6da",
            "block_header": "#ba68c8",
        }
        colors = data.get("colors", {})
        if isinstance(colors, dict) and ("dark" in colors or "light" in colors):
            legacy = colors.get("dark") or colors.get("light") or {}
            colors = {**default_colors, **legacy}
        self.colors = {
            "param": colors.get("param", default_colors["param"]),
            "prop": colors.get("prop", default_colors["prop"]),
            "block_header": colors.get("block_header", default_colors["block_header"]),
        }

    def save(self) -> None:
        """Save settings to disk."""
        write_json(CONFIG_PATH, {
            "last_pak_dir": self.last_pak_dir,
            "last_project_dir": self.last_project_dir,
            "multi_pack_files": self.multi_pack_files,
            "multi_pack_overwrite": self.multi_pack_overwrite,
            "colors": self.colors,
        })

