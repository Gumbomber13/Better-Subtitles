@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Better Subtitles - Preflight Check
echo ========================================
echo.

REM Prefer venv if present
if exist "whisperx-env" (
  call whisperx-env\Scripts\activate
)

python setup_whisperx.py --check
echo.
pause


