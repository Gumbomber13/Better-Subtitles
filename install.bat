@echo off
setlocal enabledelayedexpansion

echo ========================================
echo WhisperX One-Click Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.10 or 3.11 from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Found Python %PYTHON_VERSION%

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git not found!
    echo Please install Git from:
    echo https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)
echo [OK] Git is installed

REM Check if ffmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] ffmpeg not found!
    echo This is required for video processing.
    echo Install with: winget install ffmpeg
    echo Or download from: https://www.gyan.dev/ffmpeg/builds/
    echo.
    set /p CONTINUE="Continue without ffmpeg? (y/N): "
    if /i not "!CONTINUE!"=="y" (
        echo Installation cancelled.
        pause
        exit /b 1
    )
) else (
    echo [OK] ffmpeg is installed
)

echo.
echo ========================================
echo Starting automated setup...
echo ========================================
echo.

REM Ensure virtual environment exists
if not exist "whisperx-env" (
    echo [INFO] Creating virtual environment in whisperx-env
    python -m venv whisperx-env
)

REM Activate venv for this session
call whisperx-env\Scripts\activate

REM Run the Python setup script non-interactively
python setup_whisperx.py --yes
if errorlevel 1 (
    echo.
    echo ========================================
    echo [ERROR] Setup failed!
    echo ========================================
    echo.
    echo Try manual installation:
    echo 1. See INSTALL_MANUAL.md for step-by-step instructions
    echo 2. Or check the setup log above for specific errors
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [SUCCESS] Installation Complete!
echo ========================================
echo.
echo You can now run:
echo   whisperx-env\Scripts\activate
echo   python davinci_srt_generator.py
echo.
echo Or process videos in the 'input' folder automatically.
echo.
pause