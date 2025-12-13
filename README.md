# PakBeast

A modern tool for editing `.pak` files in **Dying Light: The Beast**. PakBeast provides an intuitive graphical interface for searching, editing, and modifying game script parameters, properties, and blocks.

## Features

- **Search & Edit**: Find and modify `Param()`, properties, and code blocks
- **Visual Editor**: Syntax-highlighted preview with intuitive editing interface
- **Project Management**: Save and load your modifications as projects
- **Multi-file Packing**: Pack multiple `.pak` files efficiently
- **Diff Comparison**: Compare original and modded PAK files to see exact changes with line numbers
- **Modern UI**: Clean, customizable interface built with CustomTkinter

## Installation

1. Clone the repository:

```bash
git clone https://github.com/PakBeast/PakBeast.git
cd PakBeast
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python main.py
```

## Building to EXE

To build a standalone Windows executable:

```bash
python -m pip install pyinstaller
python -m PyInstaller pakbeast.spec
```

Or use the build script:

```bash
build.bat
```

The executable will be in the `dist` folder.

## Usage

1. **Load a .pak file**: Click the toolbar button **Open Game Data**.
2. **Search**: Enter a parameter or property name in the search box.
3. **Edit**: Double-click any result to modify its value.
4. **Save Project**: Click the toolbar button **Save Project** (saves your edits as JSON).
5. **Pack**: Click the toolbar button **Build Mode** to create the modified `.pak` file.
6. **Compare PAKs**: Use the **Diff** tab to compare original and modded PAK files, view parameter changes, and see modified lines with line numbers.

## Keyboard Shortcuts

- **Enter**: Search for parameters
- **Ctrl+F**: Search within opened file (in preview panel)
- **Double-click**: Edit value or delete block
- **Right-click**: Context menu

## Requirements

- Python 3.8+
- customtkinter >= 5.2.0
- Pillow >= 10.0.0

## Project Structure

```
PakBeast/
├── core/          # Core application logic and models
├── dialogs/       # Dialog windows
├── operations/    # File operations, packing, searching
├── ui/            # UI components and builders
├── logic/         # Business logic (scanner)
├── main.py        # Application entry point
├── favicon.ico    # Application icon
├── pakbeast.spec  # PyInstaller configuration
└── requirements.txt
```

## Credits

- **freeloadergt**: [Nexus Mods Profile](https://next.nexusmods.com/profile/freeloadergt?gameId=8178)

## License

Copyright (C) 2025 PakBeast

See [LICENSE](LICENSE) file for details.
