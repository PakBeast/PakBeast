"""Utility functions for comparison operations."""


def _is_text(data: bytes) -> bool:
    """Heuristic to decide if bytes are text (UTF-8-ish) rather than binary."""
    if b"\x00" in data:
        return False
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def _decode_text(data: bytes) -> str:
    """Decode bytes to text, tolerating errors."""
    return data.decode("utf-8", errors="replace")
