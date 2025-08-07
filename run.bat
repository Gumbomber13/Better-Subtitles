@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Better Subtitles - Run
echo ========================================
echo.

REM If first run, install everything automatically
if not exist "whisperx-env" (
    echo [INFO] First run detected. Running installer...
    call install.bat
    goto :eof
)

REM Activate environment and run
call whisperx-env\Scripts\activate
python davinci_srt_generator.py
echo.
pause

