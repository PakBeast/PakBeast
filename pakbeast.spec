# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('favicon.ico', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Standard library modules not needed
        'unittest', 'test', 'tests', 'pydoc', 'doctest',
        'distutils', 'setuptools', 'email', 'http', 'urllib3',
        'xmlrpc', 'pdb', 'pydoc_data', 'tkinter.test',
        # Optional dependencies
        'numpy', 'scipy', 'matplotlib', 'pandas',
        # Platform-specific modules (Windows only)
        'posix', 'pwd', 'grp', 'termios', 'readline',
        'fcntl', '_posixsubprocess', '_posixshmem',
        # Other unused modules
        'asyncio',
        'sqlite3', 'dbm', 'gdbm',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PakBeast',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # Strip not available on Windows by default
    upx=False,  # disable UPX to reduce AV heuristics
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want to see console output for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='favicon.ico',  # Use favicon.ico as the executable icon
)

