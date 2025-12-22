"""
Business logic utilities for the PakBeast application.

This module contains general-purpose business logic utilities that are used across
multiple operation types. These are cross-cutting concerns that don't belong to
any specific operation but are shared functionality.

Examples:
    - scanner.py: File parsing and scanning utilities used by search, preview, and edit operations
    - Future utilities: Analysis, validation, or other general business logic

For operation-specific logic, see the operations/ folder.
"""

from .scanner import scan_scr_for_hits, find_block_bounds, _find_block_context_name

__all__ = [
    'scan_scr_for_hits',
    'find_block_bounds',
    '_find_block_context_name',
]

