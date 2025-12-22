"""File tree operations for filtering and navigation."""

import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App


def populate_tree(app: 'App', root: Path) -> None:
    """Populate the file tree with extracted files."""
    from ui.utils import shorten_path
    
    app.path_to_id.clear()
    # Root shows just the name
    root_id = app.tree.insert("", "end", text=root.name, values=(str(root),), open=True)
    app.path_to_id[root] = root_id
    app.tree.set(root_id, "abspath", str(root))
    app.tree.set(root_id, "tooltip", root.name)
    
    for dirpath, dirnames, filenames in os.walk(root):
        parent_path = Path(dirpath)
        parent_id = app.path_to_id.get(parent_path)
        if parent_id is None:
            continue
        dirnames.sort()
        filenames.sort()
        
        for name in dirnames:
            full_path = parent_path / name
            # Show just the name (tree structure shows hierarchy), but shorten very long names
            display_text = name if len(name) <= 50 else shorten_path(name, max_length=50)
            rel_path = full_path.relative_to(root) if root else Path(name)
            
            item_id = app.tree.insert(
                parent_id, "end", text=display_text, values=(str(full_path),)
            )
            app.path_to_id[full_path] = item_id
            app.tree.set(item_id, "abspath", str(full_path))
            # Store full relative path for tooltip
            app.tree.set(item_id, "tooltip", str(rel_path))
        
        for name in filenames:
            full_path = parent_path / name
            # Show just the name (tree structure shows hierarchy), but shorten very long names
            display_text = name if len(name) <= 50 else shorten_path(name, max_length=50)
            rel_path = full_path.relative_to(root) if root else Path(name)
            
            item_id = app.tree.insert(
                parent_id, "end", text=display_text, values=(str(full_path),)
            )
            app.path_to_id[full_path] = item_id
            app.tree.set(item_id, "abspath", str(full_path))
            # Store full relative path for tooltip
            app.tree.set(item_id, "tooltip", str(rel_path))


def on_file_search_change(app: 'App', *args):
    """Handle file search input changes with debouncing."""
    if app._search_after_id:
        app.after_cancel(app._search_after_id)
    app._search_after_id = app.after(300, filter_file_tree, app)


def filter_file_tree(app: 'App'):
    """Filter the file tree based on search query."""
    query = app.file_search_entry.get().lower().strip()
    app.tree.delete(*app.tree.get_children())
    if not app.temp_root:
        return
    if not query:
        populate_tree(app, app.temp_root)
        return
    paths_to_display = set()
    for path_obj in app.path_to_id:
        if query in path_obj.name.lower():
            paths_to_display.add(path_obj)
            parent = path_obj.parent
            while parent and (parent == app.temp_root or app.temp_root in parent.parents):
                paths_to_display.add(parent)
                parent = parent.parent
    from ui.utils import shorten_path
    
    filtered_path_to_id = {}
    for path in sorted(list(paths_to_display), key=lambda p: len(p.parts)):
        parent_id = "" if path == app.temp_root else filtered_path_to_id.get(path.parent, "")
        
        # Show just the name (tree structure shows hierarchy), but shorten very long names
        display_text = path.name if len(path.name) <= 50 else shorten_path(path.name, max_length=50)
        if path == app.temp_root:
            rel_path = Path(path.name)
        else:
            rel_path = path.relative_to(app.temp_root) if app.temp_root else Path(path.name)
        
        item_id = app.tree.insert(
            parent_id, "end", text=display_text, values=(str(path),), open=True
        )
        filtered_path_to_id[path] = item_id
        app.tree.set(item_id, "abspath", str(path))
        app.tree.set(item_id, "tooltip", str(rel_path))


def on_tree_select(app: 'App', _evt=None) -> None:
    """Handle tree selection event."""
    if not (sel := app.tree.selection()):
        return
    try:
        # Get path from the "abspath" column
        path_str = app.tree.set(sel[0], "abspath")
        if not path_str:
            return
        p = Path(path_str)
    except Exception:
        return
    if not p.is_dir() and app.current_file != p:
        from .preview_handler import on_tree_select_path
        on_tree_select_path(app, p)

