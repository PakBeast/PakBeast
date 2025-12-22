"""Centralized file type configuration for PakBeast."""

# Extensions that support search/editing (params, properties, blocks)
SUPPORTED_SEARCH_EXTENSIONS = [
    '.scr',   # Script files - main focus (5,572 files)
    '.ini',   # Configuration files with properties (4 files)
    '.loot',  # Loot definition files (5 files)
    '.gui',   # GUI definition files (964 files) - JSON-like
    '.cfg',   # Config files (4 files) - JSON format
    '.json',  # JSON files (4 files)
    '.txt',   # Text files (1 file)
]

# Extensions for comparison operations
SUPPORTED_COMPARISON_EXTENSIONS = [
    '.scr', '.cfg', '.json', '.txt', '.loot', '.gui', '.ini'
]

# Extensions that can be previewed in the editor
SUPPORTED_PREVIEW_EXTENSIONS = [
    '.scr', '.cfg', '.json', '.txt', '.loot', '.gui', '.ini'
]

# All text-based file extensions (for general text handling)
TEXT_FILE_EXTENSIONS = [
    '.scr', '.cfg', '.txt', '.json', '.loot', '.gui', '.def', '.ini', '.xml', '.lua'
]
