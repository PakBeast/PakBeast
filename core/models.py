"""Data models for the mod tool."""

from typing import Tuple, Literal


class ModEdit:
    """A single change: value replacement, block deletion, or line deletion."""
    
    def __init__(
        self,
        file_path: str,
        line_number: int,
        original_value: str,
        current_value: str,
        description: str,
        param_name: str,
        is_param: bool = False,
        is_enabled: bool = True,
        edit_type: Literal['VALUE_REPLACE', 'BLOCK_DELETE', 'LINE_DELETE', 'LINE_REPLACE', 'LINE_INSERT'] = 'VALUE_REPLACE',
        end_line_number: int = -1,
        insertion_index: int = 0,
    ) -> None:
        self.file_path = file_path
        self.line_number = line_number
        self.original_value = original_value
        self.current_value = current_value
        self.description = description
        self.param_name = param_name
        self.is_param = is_param
        self.is_enabled = is_enabled
        self.edit_type = edit_type
        self.end_line_number = end_line_number if end_line_number != -1 else line_number
        self.insertion_index = insertion_index

    def key(self) -> Tuple[str, int, int]:
        return (self.file_path, self.line_number, self.insertion_index)

