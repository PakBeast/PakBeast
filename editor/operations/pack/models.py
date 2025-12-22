"""Data models for packing operations."""


class PackingWarning:
    """Simple class to represent warnings during packing (not errors)."""
    def __init__(self, message: str):
        self.message = message
    def __str__(self):
        return self.message
