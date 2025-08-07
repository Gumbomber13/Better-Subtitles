# WhisperX Installation

## One-Click Installation (Recommended)

### Windows
```bash
# Double-click or run in Command Prompt:
install.bat
```

### Linux/macOS
```bash
# Run in terminal:
chmod +x install.sh && ./install.sh
```

That's it! The script will:
- ✅ Check Python 3.10/3.11 installation
- ✅ Verify Git and ffmpeg prerequisites 
- ✅ Create virtual environment automatically
- ✅ Install all dependencies (PyTorch, WhisperX, SRT)
- ✅ Test the installation

## What You Need First

**All Platforms:**
- Python 3.10 or 3.11 from https://python.org/downloads/
- Git from https://git-scm.com/downloads

**Windows:**
- ffmpeg: `winget install ffmpeg`

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git ffmpeg
```

**macOS:**
```bash
brew install python@3.11 git ffmpeg
```

## After Installation

Activate the environment and run the subtitle generator:
```bash
whisperx-env\\Scripts\\activate   # Windows
python davinci_srt_generator.py

# macOS/Linux
source whisperx-env/bin/activate
python davinci_srt_generator.py
```

Or place videos in the `input/` folder and run for batch processing.

## Troubleshooting

If automatic installation fails, see [INSTALL_MANUAL.md](INSTALL_MANUAL.md) for step-by-step manual instructions.

## What Gets Installed

- **WhisperX**: Advanced speech recognition with word-level timing
- **PyTorch**: ML framework (GPU or CPU version auto-detected)  
- **SRT Library**: Subtitle file manipulation
- **Virtual Environment**: Isolated Python environment in `whisperx-env/`