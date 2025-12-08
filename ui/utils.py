"""UI utility functions."""

import sys
import customtkinter as ctk
from pathlib import Path


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
    """Get preview text widget colors based on current theme."""
    is_dark = is_dark_mode()
    if is_dark:
        return "#1e1e1e", "#d4d4d4", "#2d2d30"  # bg, fg, highlight_bg
    else:
        return "#FFFFFF", "#000000", "#e8e8e8"  # bg, fg, highlight_bg


def set_window_icon(window: ctk.CTk | ctk.CTkToplevel) -> None:
    """
    Set the application icon on a window (main window or dialog).
    
    Args:
        window: The window to set the icon on (CTk or CTkToplevel)
    """
    try:
        # Get the path to icon.png relative to this file
        # utils.py is in pakbeast/ui/, icon.png is in pakbeast/
        icon_path = Path(__file__).parent.parent / "icon.png"
        # Convert to absolute path to ensure it's found
        icon_path = icon_path.resolve()
        
        if not icon_path.exists():
            return
        
        # For CustomTkinter windows, we need to access the underlying tkinter window
        # CTk and CTkToplevel have a 'tk' attribute that gives us the tkinter window
        tk_window = window.tk if hasattr(window, 'tk') else window
        
        # Use PIL/Pillow to load the icon (works best for PNG files on all platforms)
        try:
            from PIL import Image, ImageTk
            img = Image.open(icon_path)
            # Convert to PhotoImage and store reference to prevent garbage collection
            if not hasattr(window, '_icon_photo'):
                window._icon_photo = ImageTk.PhotoImage(img)
            # Use iconphoto which works on all platforms (Windows, Linux, macOS)
            # Set as default (True) so it applies to all windows
            tk_window.iconphoto(True, window._icon_photo)
        except ImportError:
            # Fallback: If PIL is not available, try iconbitmap (Windows-specific, works with .ico)
            if sys.platform.startswith('win'):
                try:
                    tk_window.iconbitmap(str(icon_path))
                except Exception:
                    try:
                        tk_window.wm_iconbitmap(str(icon_path))
                    except Exception:
                        pass
            else:
                # On non-Windows without PIL, try iconbitmap as last resort
                try:
                    tk_window.iconbitmap(str(icon_path))
                except Exception:
                    pass
        except Exception:
            # If PIL fails for other reasons, try fallback methods
            if sys.platform.startswith('win'):
                try:
                    tk_window.iconbitmap(str(icon_path))
                except Exception:
                    pass
    except Exception:
        # Silently fail if icon cannot be set
        pass


