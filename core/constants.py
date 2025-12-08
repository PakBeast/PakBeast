"""Constants and regex patterns for the mod tool."""

from pathlib import Path
import re

APP_NAME = "PakBeast"
APP_DIR = Path.home() / ".pakbeast"
CONFIG_PATH = APP_DIR / "config.json"

# Regexes for simple, robust matching in .scr files.
PARAM_RE = re.compile(r'Param\("([^"]+)",\s*(".*?"|\S+)\)\s*;')
# Does not match block headers and correctly ignores trailing comments.
PROP_RE = re.compile(r'^\s*(?!Param\b)(\w+)\s*\((.*?)\)\s*(?:;|\{)')
# BLOCK_HEADER_RE is for highlighting and right-click context menu (excludes Action now)
# It now excludes lines ending in a semicolon to avoid matching single-line properties.
BLOCK_HEADER_RE = re.compile(r'^\s*(AttackPreset|Item|Set|PerceptionPreset)\s*\(\s*"([^"]+)"[^)]*\)[^;]*$')
# DELETABLE_BLOCK_HEADER_RE is for default double-click deletion (excludes Action)
# It now also excludes lines ending in a semicolon.
DELETABLE_BLOCK_HEADER_RE = re.compile(r'^\s*(AttackPreset|Item|Set|PerceptionPreset)\s*\(\s*"([^"]+)"[^)]*\)[^;]*$')

