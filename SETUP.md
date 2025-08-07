================================================================================
                        WHISPERX TO DAVINCI SUBTITLE GENERATOR
================================================================================

QUICK START (After First time Setup)
-----------
1. Activate the environment
    whisperx-env\Scripts\activate
    
2. Process your videos
    python davinci_srt_generator.py

3. Done! Check output/ folder for results


FIRST TIME SETUP
----------------
1. Create virtual environment:
    python -m venv whisperx-env

2. Activate it:
    whisperx-env\Scripts\activate

3. Run automated setup:
    python setup_whisperx.py

This will:
    - Check Python version (needs 3.10 or 3.11)
    - Check for Git and ffmpeg  
    - Detect GPU and install appropriate PyTorch
    - Install WhisperX and dependencies
    - Verify everything works


DAILY USAGE
-----------
1. Activate environment:
    whisperx-env\Scripts\activate

2. Process videos:
    python davinci_srt_generator.py


CONFIGURATION FILES
-------------------

whisperx_config.py - Main settings:
    MODEL = "large-v3"        # tiny, small, medium, large-v3
    COMPUTE_TYPE = "float16"  # GPU: float16, CPU: float32
    LANGUAGE = "en"           # Language code or None
    USE_VAD = True           # Voice activity detection
    USE_DIARIZATION = False  # Speaker identification

vocabulary.txt - Custom words (one per line):
    DaVinci Resolve
    WhisperX
    [uhh]
    [um]


PROCESSING MODES
----------------
Default - Process all videos in input folder:
    python davinci_srt_generator.py

Single video:
    python davinci_srt_generator.py --mode video --input movie.mp4

Existing JSON:
    python davinci_srt_generator.py --mode json --input output/movie.json


WORKFLOW
--------
1. Place videos in:    input/
2. Run the script
3. Get results from:   output/
    - *.json = Transcription data
    - *_davinci.srt = DaVinci-optimized subtitles


TROUBLESHOOTING
---------------

Prerequisites not found:
    Python 3.10:  https://www.python.org/downloads/
    Git:          https://git-scm.com/download/win  
    ffmpeg:       winget install ffmpeg

Performance issues:
    GPU not detected:  Change COMPUTE_TYPE = "float32"
    Too slow:         Use MODEL = "medium"
    Out of memory:    Reduce BATCH_SIZE

Common errors:
    "WhisperX not found":     Re-run setup_whisperx.py
    "Path too long":          Move to C:\Whisper\
    "File not found":         Check input/ folder
    DaVinci splitting words:  Clear cache, use latest file


MANUAL SETUP (IF AUTOMATED FAILS)
----------------------------------
1. Create virtual environment:
    python -m venv whisperx-env
    whisperx-env\Scripts\activate

2. Install PyTorch:
    # For NVIDIA GPU:
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    
    # For CPU:
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

3. Install requirements:
    pip install -r requirements.txt


PROJECT STRUCTURE
-----------------
Whisper/
├── input/                    # Put videos here
├── output/                   # Results appear here
├── davinci_srt_generator.py  # Main script
├── whisperx_config.py        # Settings
├── vocabulary.txt            # Custom words
├── setup_whisperx.py         # Setup script
└── requirements.txt          # Dependencies


FEATURES
--------
✓ Batch process multiple videos
✓ Smart word grouping (1-2 words per subtitle)
✓ Frame-accurate timing for any fps
✓ Custom vocabulary support
✓ Speaker diarization (optional)
✓ Phrase boundary detection
✓ DaVinci Resolve optimized


NOTE: Always activate the virtual environment before running scripts!
    whisperx-env\Scripts\activate


================================================================================
For detailed documentation, press Ctrl+Shift+V to preview this file formatted
================================================================================