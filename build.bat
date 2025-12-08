@echo off
echo Building PakBeast executable...
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
)

echo.
echo Building executable...
python -m PyInstaller pakbeast.spec

echo.
echo Build complete! Check the 'dist' folder for PakBeast.exe
pause

