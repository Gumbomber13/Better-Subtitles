# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Purpose

This is a DaVinci Resolve-optimized subtitle generation system for video editors. The workflow processes audio/video files through WhisperX and creates precisely-timed SRT files that work seamlessly in DaVinci Resolve.

**Key Features:**
- Word-level subtitle timing with DaVinci Resolve compatibility
- Intelligent word grouping (1-2 words per subtitle) for natural reading flow
- Frame-accurate timing at 23.976 FPS with proper overlap handling
- Eliminates DaVinci's "dead frame" gaps through strategic overlapping
- Configurable separators for different DaVinci behavior preferences

## Timing Algorithm

The system implements sophisticated gap-based timing rules specifically designed for DaVinci Resolve's "exclusive end" subtitle model:

- **Continuous Speech (<208.54ms gaps)**: Creates overlapping subtitles to prevent visual gaps
- **Natural Pauses (~208.54ms/5 frames)**: Maintains clean 2-frame gaps for speech rhythm
- **Long Pauses (>208.54ms)**: Extends subtitles 2 frames past next start for visual continuity
- **Frame Alignment**: All timing snapped to exact 23.976 FPS boundaries (41.71ms precision)

## Project Overview

This is a WhisperX-based audio transcription project that processes audio/video files and generates various subtitle formats. The main functionality includes:

- Audio transcription using WhisperX (advanced Whisper implementation with speaker diarization and word-level timestamps)
- Generation of word-level SRT subtitles from WhisperX JSON output
- Support for multiple output formats (JSON, SRT, TSV, TXT, VTT)

## Python Environment Setup

This project uses a virtual environment located in `whisperx-env/`:

**Activate the environment:**
```bash
# Windows
whisperx-env\Scripts\activate

# Deactivate
deactivate
```

**Key dependencies available:**
- `whisperx` - Main transcription engine
- `srt` - SRT subtitle manipulation library
- Various ML/AI tools (transformers, torch, numpy, etc.)

## Core Architecture

### Main Script: `davinci_srt_generator.py`

**Purpose**: DaVinci Resolve-optimized SRT generator that creates seamless subtitle experiences.

**Core Components:**
- **DaVinciSRTGenerator Class**: Main processing engine with configurable FPS and overlap settings
- **Word Grouping Engine**: Intelligent 1-2 word phrase creation based on linguistic rules
- **Timing Calculator**: Frame-perfect timing with gap-based rule application
- **Separator System**: Configurable word separators for DaVinci compatibility testing

**Processing Pipeline:**
1. **WhisperX JSON Input**: Extracts word-level timestamps with confidence scores
2. **Word Grouping**: Groups words into natural phrases using linguistic rules:
   - Prepositions/articles always group with following words
   - Common phrases stay together ("bit of", "used to", etc.)
   - Emphasized words (>250ms duration) stand alone
   - Punctuation creates natural breaks
3. **Frame Alignment**: Converts timestamps to exact 23.976 FPS boundaries
4. **Gap Analysis**: Applies timing rules based on speech pattern gaps
5. **Overlap Generation**: Creates strategic overlaps to eliminate DaVinci dead frames

### Data Flow
1. Audio/video file → WhisperX → JSON output with word-level timestamps and confidence scores
2. JSON → `davinci_srt_generator.py` → DaVinci-optimized SRT file
3. Multiple WhisperX formats available in `output/` directory

### File Structure
- `whisperx-env/` - Python virtual environment with all dependencies
- `davinci_srt_generator.py` - Main DaVinci Resolve SRT generator
- `output/` - Contains all generated transcription files
  - `*.json` - WhisperX output with word-level timing and confidence scores
  - `*.srt` - Standard sentence-level subtitles from WhisperX
  - `*.tsv`, `*.txt`, `*.vtt` - Additional WhisperX output formats
  - `*_davinci_seamless.srt` - Generated DaVinci-optimized subtitles

## Common Development Tasks

**Run WhisperX transcription:**
```bash
# Activate environment first
whisperx-env\Scripts\activate

# Process audio/video file
whisperx input_file.mp4 --output_dir output --output_format json,srt,tsv,txt,vtt
```

**Generate DaVinci-optimized subtitles:**
```bash
# Activate environment first
whisperx-env\Scripts\activate

# Run the DaVinci SRT generator
python davinci_srt_generator.py
```

**Install additional dependencies:**
```bash
# Activate environment first
whisperx-env\Scripts\activate
pip install package_name
```

## Key Technical Details

### Frame-Based Configuration
- **FPS**: 23.976 (exact NTSC film rate: 24000/1001 fraction)
- **Frame Duration**: 41.71ms per frame (exact calculation)
- **Overlap**: 10ms standard overlap to prevent DaVinci dead frames
- **Min Duration**: 2 frames minimum subtitle duration (83.42ms)
- **Frame Precision**: All timestamps aligned to exact frame boundaries

### Advanced Timing Algorithm
The system implements a sophisticated three-tier timing strategy:

1. **Gap-Based Rules (Priority)**:
   - ~208.54ms gaps (5 frames): Create 2-frame clean gap for natural speech rhythm
   - >208.54ms gaps: Extend subtitle 2 frames past next start for visual continuity
   - <208.54ms gaps: Fall through to overlap strategy

2. **Overlap Strategy**: For continuous speech, create 10ms+ overlaps to prevent visual gaps in DaVinci Resolve's "exclusive end" timing model

3. **Frame Boundary Snapping**: All start/end times aligned to exact frame boundaries for perfect DaVinci integration

### Word Grouping Intelligence
The system uses linguistic rules to create natural subtitle groupings:

**Priority Grouping Logic**:
1. **Never group after punctuation** (creates sentence boundaries)
2. **Always group prepositions/articles** with following words (overrides duration limits)
3. **Keep common phrases together** ("bit of", "used to", "kind of", etc.)
4. **Respect emphasized words** (>250ms duration stand alone, except prepositions)
5. **Handle proper nouns** (capitalized words often stand alone)

**Configurable Separators**:
- Regular space `" "` (default, may split in DaVinci)
- No separator `""` (creates compound words: "Idid", "alittle")
- Visible separators `"_"`, `"-"`, `"·"` (testing alternatives)
- Unicode separators (invisible word joiners)

### Data Processing
- **Flattened Structure**: Words extracted from all segments into single processing array
- **Confidence Scoring**: WhisperX provides word-level confidence scores (0.0-1.0)
- **Encoding**: UTF-8 for international character support
- **Statistics Tracking**: Real-time grouping and timing strategy analytics

## Testing and Validation

**DaVinci Integration Testing**:
1. **Frame Accuracy**: Verify all timestamps align to 41.71ms boundaries (23.976 FPS)
2. **Visual Gap Elimination**: Confirm no visible gaps between subtitles in DaVinci timeline
3. **Overlap Validation**: Check that overlapping subtitles display correctly (no flicker)
4. **Word Grouping Quality**: Verify natural phrase groupings and separator behavior
5. **Timing Strategy Distribution**: Review statistics output for proper gap handling

**Quality Validation**:
- **Content Integrity**: All words preserved from WhisperX transcription
- **SRT Format**: Valid subtitle numbering, timing format, and UTF-8 encoding
- **Duration Limits**: No subtitles shorter than 2 frames or longer than 3 seconds (unless unavoidable)
- **Confidence Analysis**: Review low-confidence words that may need manual review

## Configuration Customization

**Modify timing behavior in `davinci_srt_generator.py`**:

```python
# Frame rate configuration (exact NTSC film rate)
fps_fraction = Fraction(24000, 1001)  # 23.976 FPS exactly

# Timing adjustments
overlap_ms = 10.0                     # Overlap for continuous speech
min_duration_ms = 2 * frame_duration_ms  # Minimum subtitle duration

# Gap-based thresholds (in milliseconds)
FIVE_FRAMES_MS = 208.54               # Natural pause detection
TWO_FRAMES_MS = 83.42                 # Clean gap creation
```

**Word grouping behavior**:
```python
EMPHASIS_DURATION_MS = 250            # Threshold for emphasized/standalone words
SEPARATOR = " "                       # Word separator (configurable)
```

**File path configuration**:
```python
input_file = "output/arcade.json"             # WhisperX JSON input
output_file = "output/arcade_davinci_seamless.srt"  # SRT output
```

## Important Notes

- **File paths**: Script currently hardcodes input/output paths - modify `main()` function for different files
- **DaVinci Compatibility**: Designed specifically for DaVinci Resolve's subtitle behavior and timing requirements
- **Performance**: WhisperX benefits from GPU acceleration for faster transcription
- **Separator Testing**: Try different separator options if subtitles split incorrectly in DaVinci:
  - `SEPARATOR = ""` for compound words (most reliable)
  - `SEPARATOR = "_"` or `"-"` for visible separators
  - `SEPARATOR = "·"` for middle dot separation
  
**Accuracy Factors**:
- **Audio Quality**: Clear speech with minimal background noise yields best results
- **WhisperX Model**: Confidence scores indicate word-level accuracy (review <0.5 scores)
- **Frame Rate Matching**: System optimized for 23.976 FPS (standard film rate)
- **Speech Patterns**: Gap-based timing works best with natural speech rhythms

**DaVinci Integration Tips**:
- Import generated SRT as subtitle track
- Subtitles should appear as individual clips without gaps
- Each phrase should be a single subtitle element
- Overlapping timing prevents visual gaps without display issues