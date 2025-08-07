# Installation Instructions

## Quick Start (Recommended)

1. Install Python 3.10 from https://www.python.org/downloads/
2. Install Git from https://git-scm.com/download/win
3. Install ffmpeg: `winget install ffmpeg`
4. Run the setup script:
   ```bash
   python setup_whisperx.py
   ```

## Manual Installation

If the setup script doesn't work:

### 1. Create virtual environment
```bash
python -m venv whisperx-env
whisperx-env\Scripts\activate
```

### 2. Install PyTorch (choose one)

**For NVIDIA GPU:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**For CPU only:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 3. Install WhisperX
```bash
pip install -r requirements.txt
```

## Troubleshooting

### "Git not found"
Install Git from https://git-scm.com/download/win

### "ffmpeg not found"  
Download from https://www.gyan.dev/ffmpeg/builds/
Extract and add to PATH

### GPU not detected
- Use `float32` instead of `float16` in whisperx_config.py
- Or install CPU version of PyTorch

### Installation fails
Try minimal install:
```bash
pip install git+https://github.com/m-bain/whisperx.git
pip install srt
```