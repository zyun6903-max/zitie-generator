@echo off
chcp 65001 >nul

echo ========================================
echo   Zitie Generator - Windows Build
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install Python 3.10+ first.
    echo        Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
if not exist venv (
    python -m venv venv
)

echo [2/5] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] pip install failed
    pause
    exit /b 1
)

echo [3/5] Generating icon...
python generate_icon.py

echo [4/5] Building with PyInstaller...
pip install pyinstaller
pyinstaller build.spec
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller build failed
    pause
    exit /b 1
)

echo [5/5] Building NSIS installer...
if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    "C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
    echo Done! Installer created at: dist\字帖生成器_安装包.exe
) else (
    echo [INFO] NSIS not found - skipping installer
    echo Portable exe available at: dist\字帖生成器\字帖生成器.exe
)

echo.
echo ========================================
echo   Build complete!
echo ========================================
pause
