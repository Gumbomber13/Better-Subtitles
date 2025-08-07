### Better Subtitles (WhisperX → DaVinci Resolve)

Make clean, perfectly-timed SRT subtitles for DaVinci Resolve from your videos — with one click.

### Prerequisites (once per computer)
- Python 3.10 or 3.11
- Git
- ffmpeg
- Windows: Microsoft Visual C++ Redistributable 2015–2022 (x64)

Windows (PowerShell):

```powershell
winget install git
winget install ffmpeg
winget install Microsoft.VCRedist.2015+.x64
```

macOS (Homebrew):

```bash
brew install git ffmpeg python@3.11
```

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git ffmpeg
```

### The super simple way
- Windows: Double‑click `install.bat`
- Mac/Linux: Run these in Terminal from the project folder:

```bash
chmod +x install.sh
./install.sh
```

What happens next:
- The installer sets everything up for you and starts processing automatically.
- Put your videos in the `input/` (or `Input/`) folder. Results appear in `output/` as `yourvideo_davinci.srt`.
- You can stop anytime with Ctrl+C and run it again later.

### Using it again later
Windows:

```powershell
whisperx-env\Scripts\activate
python davinci_srt_generator.py
```

Mac/Linux:

```bash
source whisperx-env/bin/activate
python davinci_srt_generator.py
```

### Tips
- Works with: mp4, mov, mkv, avi, webm, m4v, wmv, flv, 3gp
- Put files in `input/` before running, or add them and run again.
- SRTs are tuned for DaVinci Resolve, with smooth timing and clean grouping.

### If something doesn’t start
- Windows: try double‑clicking `install.bat` again.
- Mac/Linux: run the two commands again:

```bash
chmod +x install.sh
./install.sh
```

- Still nothing? Open a terminal in the folder and run:

```bash
python setup_whisperx.py --yes --run
```

### Check my setup (optional)
- Windows: double‑click `preflight.bat`
- Mac/Linux:
  ```bash
chmod +x preflight.sh
./preflight.sh
  ```
This will check for Python, Git, ffmpeg, and that `whisperx`/`srt` are installed and callable.

### Change settings (optional)
- Open `whisperx_config.py` to change model, language, or options like diarization.
- You can also add custom words in `vocabulary.txt` (one per line).

That’s it — drop in videos, get SRTs in `output/`, import into DaVinci Resolve.