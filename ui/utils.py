"""UI utility functions."""

import sys
import customtkinter as ctk
from pathlib import Path
from functools import lru_cache
from typing import Optional, Tuple


def shorten_path(path: str | Path, max_length: int = 50) -> str:
    """
    Shorten a file path by showing the beginning and end parts with '...' in the middle.
    
    Args:
        path: The path to shorten (string or Path object)
        max_length: Maximum length for the shortened path (default: 50)
    
    Returns:
        Shortened path string
    """
    path_str = str(path)
    if len(path_str) <= max_length:
        return path_str
    
    # Convert to Path to work with parts
    path_obj = Path(path_str)
    parts = path_obj.parts
    
    if len(parts) <= 2:
        # Very short path, just truncate with ellipsis
        return path_str[:max_length - 3] + "..."
    
    # Try to include beginning and end parts
    if len(parts) == 3:
        # Simple case: first/last
        return f"{parts[0]}/.../{parts[-1]}"
    elif len(parts) == 4:
        # Show first and last two
        return f"{parts[0]}/.../{parts[-2]}/{parts[-1]}"
    else:
        # For longer paths, show first part, ..., and last two parts
        first = parts[0]
        last_two = f"{parts[-2]}/{parts[-1]}"
        remaining = max_length - len(first) - len(last_two) - 3  # 3 for "/.../"
        
        if remaining > 5:
            # Can fit more from the middle
            middle_parts = parts[1:-2]
            if middle_parts:
                middle_str = "/".join(middle_parts[:2])  # Take first 2 middle parts
                if len(middle_str) > remaining:
                    middle_str = middle_str[:remaining - 3] + "..."
                return f"{first}/{middle_str}/.../{last_two}"
        
        # Just show first and last parts
        return f"{first}/.../{last_two}"


def is_dark_mode() -> bool:
    """Check if current appearance mode is dark."""
    current_mode = ctk.get_appearance_mode()
    if current_mode == "Dark":
        return True
    elif current_mode == "Light":
        return False
    else:  # System mode
        # Try to detect system theme
        try:
            import tkinter as tk
            test_root = tk.Tk()
            test_root.withdraw()
            bg = test_root.cget("bg")
            test_root.destroy()
            # Dark themes typically have darker backgrounds
            dark_bgs = ["#212121", "#1e1e1e", "#2b2b2b", "#1f1f1f"]
            return any(bg.lower() == dbg.lower() for dbg in dark_bgs) or int(bg[1:3], 16) < 0x40 if len(bg) == 7 and bg[0] == "#" else False
        except:
            return False


def get_listbox_colors() -> tuple[str, str, str]:
    """Get listbox colors based on current theme."""
    is_dark = is_dark_mode()
    if is_dark:
        return "#212121", "#FFFFFF", "#1f538d"  # bg, fg, selectbg
    else:
        return "#FFFFFF", "#000000", "#0078d4"  # bg, fg, selectbg


def get_preview_colors() -> tuple[str, str, str]:
    """Get preview text widget colors for dark theme."""
    return "#1e1e1e", "#d4d4d4", "#3d4a2d"  # bg, fg, highlight_bg (darker yellow/green for selected edit)


_ICON_PHOTO = None


@lru_cache(maxsize=1)
def _resolve_icon_path() -> Optional[Path]:
    """Return the best icon path, checking frozen (_MEIPASS) and project root."""
    candidates = []
    try:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base = Path(sys._MEIPASS)
            candidates.append(base / "favicon.ico")
            candidates.append(base / "icon.ico")
    except Exception:
        pass
    base = Path(__file__).parent.parent
    candidates.append(base / "favicon.ico")
    candidates.append(base / "icon.ico")
    for path in candidates:
        if path.exists():
            return path.resolve()
    return None


@lru_cache(maxsize=1)
def _load_icon_photo() -> Tuple[Optional[object], Optional[Path]]:
    """Load and cache the icon image as PhotoImage (PIL preferred, tk fallback)."""
    icon_path = _resolve_icon_path()
    if not icon_path:
        return None, None
    photo = None
    if icon_path.suffix.lower() == ".png":
        try:
            from PIL import Image, ImageTk

            img = Image.open(icon_path)
            photo = ImageTk.PhotoImage(img)
        except Exception:
            try:
                import tkinter as tk

                photo = tk.PhotoImage(file=str(icon_path))
            except Exception:
                photo = None
    return photo, icon_path


def set_window_icon(window: ctk.CTk | ctk.CTkToplevel) -> None:
    """
    Set the application icon on a window (main window or dialog).
    
    Args:
        window: The window to set the icon on (CTk or CTkToplevel)
    """
    try:
        tk_window = window.tk if hasattr(window, "tk") else window
        photo_info = _load_icon_photo()
        photo = None
        icon_path = None
        if photo_info:
            photo, icon_path = photo_info

        if photo is not None:
            window._icon_photo = photo  # prevent GC
            tk_window.iconphoto(True, window._icon_photo)
            # Also set as default root icon if available
            try:
                import tkinter as tk

                if tk._default_root:
                    tk._default_root.iconphoto(True, window._icon_photo)
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


