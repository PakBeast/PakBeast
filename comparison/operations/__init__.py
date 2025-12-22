"""Comparison operations module for comparing TXT files."""

from .models import FileDiff
from .text_comparison import compare_plain_text_files
from .comparison_runner import run_comparison, parse_file_path

__all__ = [
    'FileDiff',
    'compare_plain_text_files',
    'run_comparison',
    'parse_file_path',
]
