@echo off
REM Quick start script for Kick Clip Generator (Windows)

echo ========================================
echo Kick Clip Generator
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: FFmpeg is not installed or not in PATH
    echo Please install FFmpeg for video processing
    echo Download from: https://ffmpeg.org/download.html
    echo.
    pause
)

REM Check if requirements are installed
echo Checking dependencies...
python -c "import gradio" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting Gradio interface...
echo.
echo The interface will open at: http://localhost:7860
echo Press Ctrl+C to stop the server
echo.

python main.py --gui

pause
