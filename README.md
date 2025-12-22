# PakBeast

A modern GUI tool for editing `.pak` files in **Dying Light: The Beast**. Search, edit, and modify game script parameters, properties, and blocks with an intuitive interface.

## Features

- **Search & Edit**: Find and modify `Param()`, properties, and code blocks across `.scr`, `.ini`, `.loot`, `.gui`, `.cfg`, `.json`, and `.txt` files
- **Visual Editor**: Syntax-highlighted preview with intuitive editing interface
- **Project Management**: Save and load modifications as `.pbm` project files
- **File Comparison**: Compare exported TXT files with detailed change tracking
- **Build Mods**: Compile edits into modified `.pak` files
- **Modern UI**: Clean, customizable interface built with CustomTkinter

## Installation

### Download
Download the latest release from [GitHub Releases](https://github.com/PakBeast/PakBeast/releases).

### Build from Source
```bash
# Install dependencies
pip install -r requirements.txt

# Build executable
python -m PyInstaller pakbeast.spec --clean
```

**Requirements:**
- Python 3.8+
- customtkinter >= 5.2.0
- Pillow >= 10.0.0
- pefile >= 2023.2.7

## Usage

1. **Load**: Click **Open Game Data** to extract and browse files from a `.pak` file
2. **Search**: Enter keywords to find parameters, properties, and blocks
3. **Edit**: Double-click any result or preview line to modify values
4. **Build**: Click **Build Mod** to compile edits into a modified `.pak` file

**Tips:**
- Save your work as a `.pbm` project file for later use
- Export files as TXT and use the **Comparison** tab to view differences

## Keyboard Shortcuts

- **Enter**: Search for parameters
- **Ctrl+F**: Search within opened file (preview panel)
- **Double-click**: Edit value or delete block
- **Right-click**: Context menu

## Credits

- **freeloadergt**: [Nexus Mods Profile](https://next.nexusmods.com/profile/freeloadergt?gameId=8178)

## License

Copyright (C) 2025 PakBeast

See [LICENSE](LICENSE) file for details.
