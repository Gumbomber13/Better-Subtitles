"""
WhisperX Configuration File
==========================
Modify the settings below to customize WhisperX behavior.
Uncomment the option you want to use for each setting.
"""


# ============================================================================
# PERFORMANCE COMPARISON GUIDE
# ============================================================================
"""
┌─────────────────────────┬────────┬──────────┬─────────────────────────┐
│ Model + Compute Type    │ Speed  │ Quality  │ Use Case               │
├─────────────────────────┼────────┼──────────┼─────────────────────────┤
│ large-v3 + float32     │ ★☆☆☆☆ │ ★★★★★   │ Maximum accuracy        │
│ large-v3 + float16     │ ★★★☆☆ │ ★★★★★   │ ⭐ RECOMMENDED         │
│ large-v3 + int8        │ ★★★★☆ │ ★★★★☆   │ Quick processing       │
│ large-v2 + float32     │ ★☆☆☆☆ │ ★★★★☆   │ Legacy/stable          │
│ medium + float16       │ ★★★★☆ │ ★★★☆☆   │ Fast turnaround        │
│ small + float16        │ ★★★★★ │ ★★☆☆☆   │ Quick preview          │
│ tiny + int8            │ ★★★★★ │ ★☆☆☆☆   │ Draft only             │
└─────────────────────────┴────────┴──────────┴─────────────────────────┘

Processing Time Estimates (for 10-minute video):
- large-v3 + float32: ~5-8 minutes
- large-v3 + float16: ~2-4 minutes (RECOMMENDED)
- medium + float16: ~1-2 minutes
- small + float16: ~30-60 seconds
"""

# ============================================================================
# MODEL SELECTION
# ============================================================================
# Uncomment ONE model option:

MODEL = "large-v3"        # Best quality, latest model (Nov 2023)
# MODEL = "large-v2"      # Previous version, very stable
# MODEL = "medium"        # 2x faster than large, slight quality loss
# MODEL = "small"         # 5x faster than large, noticeable quality loss
# MODEL = "tiny"          # 10x faster, draft quality only

# ============================================================================
# COMPUTE TYPE
# ============================================================================
# Uncomment ONE compute type based on your hardware:

# For NVIDIA GPU (CUDA):
# COMPUTE_TYPE = "float16"   # Fast with minimal quality loss (RECOMMENDED)
# COMPUTE_TYPE = "int8_float16"  # Fastest, slight quality loss
# COMPUTE_TYPE = "float32"  # Slower but maximum precision

# For CPU only:
COMPUTE_TYPE = "float32"  # Best quality on CPU
# COMPUTE_TYPE = "int8"     # Faster on CPU, some quality loss

# ============================================================================
# LANGUAGE SETTINGS
# ============================================================================
# Set to specific language code for faster processing, or None for auto-detect

LANGUAGE = "en"           # English (fastest if you know the language)
# LANGUAGE = None         # Auto-detect (slower but works for any language)
# LANGUAGE = "es"         # Spanish
# LANGUAGE = "fr"         # French  
# LANGUAGE = "de"         # German
# LANGUAGE = "it"         # Italian
# LANGUAGE = "pt"         # Portuguese
# LANGUAGE = "ja"         # Japanese
# LANGUAGE = "ko"         # Korean
# LANGUAGE = "zh"         # Chinese

# ============================================================================
# VOICE ACTIVITY DETECTION (VAD)
# ============================================================================
# VAD removes non-speech segments (silence, music, noise)
# This prevents hallucinated text and improves subtitle timing

USE_VAD = True            # RECOMMENDED: Cleaner output
# USE_VAD = False         # Disable if you want to transcribe everything

# VAD Sensitivity (only used if USE_VAD = True)
VAD_ONSET = 0.500        # Speech detection threshold (0.0-1.0)
                         # Lower = more sensitive (more speech detected)
                         # Higher = less sensitive (less false positives)
                         
VAD_OFFSET = 0.363       # Speech end threshold (0.0-1.0)  
                         # Lower = speech ends earlier
                         # Higher = speech extends longer

# ============================================================================
# SPEAKER DIARIZATION
# ============================================================================
# Identifies and labels different speakers (e.g., "SPEAKER_00", "SPEAKER_01")
# Note: Significantly increases processing time

USE_DIARIZATION = False   # Set to True for multi-speaker content
# USE_DIARIZATION = True  

# Number of speakers (only used if USE_DIARIZATION = True)
MIN_SPEAKERS = 1         # Minimum expected speakers
MAX_SPEAKERS = 4         # Maximum expected speakers

# HuggingFace token for speaker diarization (required if USE_DIARIZATION = True)
# Get your token from: https://huggingface.co/settings/tokens
HF_TOKEN = ""         # Replace with "your-token-here" if using diarization

# ============================================================================
# ALIGNMENT MODEL
# ============================================================================
# Model for word-level timestamp alignment

ALIGN_MODEL = "WAV2VEC2_ASR_LARGE_LV60K_960H"  # Best for English
# ALIGN_MODEL = None      # Use default for your language

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================

# Batch size for transcription (lower if running out of memory)
BATCH_SIZE = 16          # Default: 16, reduce to 8 or 4 if OOM errors

# Temperature for sampling (affects randomness/creativity)
TEMPERATURE = 0          # 0 = deterministic, higher = more creative

# Suppress specific tokens/words
SUPPRESS_TOKENS = ["♪", "♫", "[Music]", "[music]", "(Music)", "(music)"]

INITIAL_PROMPT = None

# ============================================================================
# OUTPUT SETTINGS
# ============================================================================
OUTPUT_FORMAT = "json"   # Required for word-level timing, don't change

# ============================================================================
# QUICK PRESETS
# ============================================================================
"""
To use a preset, uncomment all lines in that section:

# PRESET: Maximum Quality (Slow)
# MODEL = "large-v3"
# COMPUTE_TYPE = "float32"
# USE_VAD = True
# USE_DIARIZATION = False

# PRESET: Balanced (RECOMMENDED)
# MODEL = "large-v3"  
# COMPUTE_TYPE = "float16"
# USE_VAD = True
# USE_DIARIZATION = False

# PRESET: Fast Draft
# MODEL = "medium"
# COMPUTE_TYPE = "int8_float16"
# USE_VAD = True
# USE_DIARIZATION = False

# PRESET: Multi-Speaker Interview
# MODEL = "large-v3"
# COMPUTE_TYPE = "float16"
# USE_VAD = True
# USE_DIARIZATION = True
# MIN_SPEAKERS = 2
# MAX_SPEAKERS = 4
"""

def get_config_summary():
    """Return a summary of current configuration."""
    summary = f"""
Current WhisperX Configuration:
==============================
Model: {MODEL}
Compute Type: {COMPUTE_TYPE}
Language: {LANGUAGE if LANGUAGE else 'Auto-detect'}
VAD: {'Enabled' if USE_VAD else 'Disabled'}
Diarization: {'Enabled' if USE_DIARIZATION else 'Disabled'}
    """
    return summary.strip()

# Simple vocabulary loader - reads vocabulary.txt if it exists
import os

if os.path.exists("vocabulary.txt"):
    with open("vocabulary.txt", 'r', encoding='utf-8') as f:
        vocab_lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if vocab_lines:
        INITIAL_PROMPT = " ".join(vocab_lines[:50])  # Use first 50 terms
        print(f"Loaded {len(vocab_lines)} terms from vocabulary.txt")

if __name__ == "__main__":
    print(get_config_summary())