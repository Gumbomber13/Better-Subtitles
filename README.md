### Better Subtitles (WhisperX → DaVinci Resolve)

Make clean, perfectly-timed SRT subtitles for DaVinci Resolve from your videos — with one click.

### The super simple way
- Windows: Double‑click `install.bat`
- Mac/Linux: Run this in Terminal from the project folder:
  ```bash
chmod +x install.sh && ./install.sh
  ```

What happens next:
- The installer sets everything up for you and starts processing automatically.
- Put your videos in the `input/` (or `Input/`) folder. Results appear in `output/` as `yourvideo_davinci.srt`.
- You can stop anytime with Ctrl+C and run it again later.

### Using it again later
- Windows:
  ```
whisperx-env\Scripts\activate
python davinci_srt_generator.py
  ```
- Mac/Linux:
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
- Mac/Linux: run `chmod +x install.sh && ./install.sh` again.
- Still nothing? Open a terminal in the folder and run:
  ```bash
python setup_whisperx.py --yes --run
  ```

### Change settings (optional)
- Open `whisperx_config.py` to change model, language, or options like diarization.
- You can also add custom words in `vocabulary.txt` (one per line).

That’s it — drop in videos, get SRTs in `output/`, import into DaVinci Resolve.