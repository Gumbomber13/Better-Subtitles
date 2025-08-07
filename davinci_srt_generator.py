#!/usr/bin/env python3
"""
DaVinci Resolve SRT Generator for WhisperX with integrated processing
Complete pipeline: video → WhisperX → DaVinci-optimized SRT subtitles
"""

import json
import srt
from datetime import timedelta
from fractions import Fraction
import subprocess
import argparse
import glob
from pathlib import Path
import os
import sys

# Import configuration
try:
    from whisperx_config import *
except ImportError:
    print("Warning: whisperx_config.py not found. Using default settings.")
    # Fallback defaults if config file is missing
    MODEL = "large-v3"
    COMPUTE_TYPE = "float16"
    LANGUAGE = "en"
    USE_VAD = True
    VAD_ONSET = 0.500
    VAD_OFFSET = 0.363
    USE_DIARIZATION = False
    MIN_SPEAKERS = 1
    MAX_SPEAKERS = 4
    ALIGN_MODEL = "WAV2VEC2_ASR_LARGE_LV60K_960H"
    BATCH_SIZE = 16
    TEMPERATURE = 0
    SUPPRESS_TOKENS = ["♪", "♫", "[Music]", "[music]", "(Music)", "(music)"]
    INITIAL_PROMPT = None
    OUTPUT_FORMAT = "json"
    HF_TOKEN = None
    
    def get_config_summary():
        return f"""
Current WhisperX Configuration (defaults):
==============================
Model: {MODEL}
Compute Type: {COMPUTE_TYPE}
Language: {LANGUAGE if LANGUAGE else 'Auto-detect'}
VAD: {'Enabled' if USE_VAD else 'Disabled'}
Diarization: {'Enabled' if USE_DIARIZATION else 'Disabled'}
        """.strip()


def get_video_fps(video_path):
    """
    Automatically detect video frame rate using ffprobe.
    
    Args:
        video_path: Path to video file
        
    Returns:
        float: Frame rate (e.g., 23.976, 60.0, 29.97)
    """
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_streams', str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        for stream in data['streams']:
            if stream['codec_type'] == 'video':
                # Parse frame rate (e.g., "60/1" or "60000/1001" or "24000/1001")
                fps_str = stream.get('r_frame_rate', '24000/1001')
                num, den = map(float, fps_str.split('/'))
                fps = num / den
                
                # Round common frame rates to standard values
                if abs(fps - 23.976) < 0.01:
                    return 23.976
                elif abs(fps - 29.97) < 0.01:
                    return 29.97
                elif abs(fps - 59.94) < 0.01:
                    return 59.94
                else:
                    return round(fps, 3)
        
        print("Warning: Could not detect frame rate, using default 23.976")
        return 23.976
        
    except (subprocess.CalledProcessError, FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        print(f"Warning: ffprobe not found or failed ({e}), using default 23.976 fps")
        return 23.976


class DaVinciSRTGenerator:
    def __init__(self, fps=None, quiet=False):
        """
        Initialize with dynamic frame-based timing.
        
        Args:
            fps: Frame rate (if None, will be auto-detected from video)
            quiet: Suppress initialization output
        """
        # Store fps (will be set later if None)
        self.fps = fps
        self.quiet = quiet
        
        # Frame-based constants (in frames, not milliseconds)
        self.PHRASE_GAP_FRAMES = 5      # Frames to consider phrase boundary
        self.EXTENSION_FRAMES = 2       # Frames to extend at phrase end  
        self.MIN_DURATION_FRAMES = 2    # Minimum subtitle duration
        self.EMPHASIS_FRAMES = 6        # Frames to consider word emphasized
        
        # Fixed millisecond values (not frame-dependent)
        self.overlap_ms = 10            # Small overlap between subtitles
        self.max_gap_ms = 500           # Max gap for word grouping
        
        # DaVinci Resolve separator configuration
        self.SEPARATOR = " "  # Normal space - should work now that cache is cleared
        
        # Will be calculated once fps is known
        self.frame_duration_ms = None
        self.phrase_gap_threshold_ms = None
        self.extension_ms = None
        self.min_duration_ms = None
        self.emphasis_duration_ms = None
        
        if fps:
            self._calculate_timing_values()
            
    def _calculate_timing_values(self):
        """Calculate all frame-based timing values from fps."""
        self.frame_duration_ms = 1000.0 / self.fps
        
        # Convert frame counts to milliseconds
        self.phrase_gap_threshold_ms = self.PHRASE_GAP_FRAMES * self.frame_duration_ms
        self.extension_ms = self.EXTENSION_FRAMES * self.frame_duration_ms
        self.min_duration_ms = self.MIN_DURATION_FRAMES * self.frame_duration_ms
        self.emphasis_duration_ms = self.EMPHASIS_FRAMES * self.frame_duration_ms
        
        if not self.quiet:
            print(f"Frame rate: {self.fps} fps")
            print(f"  Frame duration: {self.frame_duration_ms:.3f}ms")
            print(f"  Phrase gap: {self.phrase_gap_threshold_ms:.3f}ms ({self.PHRASE_GAP_FRAMES} frames)")
            print(f"  Extension: {self.extension_ms:.3f}ms ({self.EXTENSION_FRAMES} frames)")
            print(f"  Min duration: {self.min_duration_ms:.3f}ms ({self.MIN_DURATION_FRAMES} frames)")
            print(f"  Emphasis threshold: {self.emphasis_duration_ms:.3f}ms ({self.EMPHASIS_FRAMES} frames)")
    
    def set_fps(self, fps):
        """Set frame rate and recalculate timing values."""
        self.fps = fps
        self._calculate_timing_values()

    def run_whisperx(self, video_path, output_dir="output"):
        """Run WhisperX using settings from whisperx_config.py"""
        # Show current configuration
        print(get_config_summary())
        print()
        
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Get video name without extension for output file naming
        video_name = Path(video_path).stem
        
        # Build WhisperX command with configuration
        cmd = [
            "whisperx", str(video_path),
            "--model", MODEL,
            "--output_dir", str(output_dir),
            "--compute_type", COMPUTE_TYPE,
            "--output_format", OUTPUT_FORMAT
        ]
        
        # Add alignment model if specified
        if ALIGN_MODEL:
            cmd.extend(["--align_model", ALIGN_MODEL])
        
        # Add alignment padding to extend alignment window

        # Add language if specified
        if LANGUAGE:
            cmd.extend(["--language", LANGUAGE])
        
        # Add VAD settings if enabled
        if USE_VAD:
            cmd.extend([
                "--vad_onset", str(VAD_ONSET),
                "--vad_offset", str(VAD_OFFSET)
            ])
        
        # Add diarization if enabled
        if USE_DIARIZATION:
            cmd.extend([
                "--diarize",
                "--min_speakers", str(MIN_SPEAKERS),
                "--max_speakers", str(MAX_SPEAKERS)
            ])
            if HF_TOKEN:
                cmd.extend(["--hf_token", HF_TOKEN])
        
        # Add advanced settings
        cmd.extend([
            "--batch_size", str(BATCH_SIZE),
            "--temperature", str(TEMPERATURE)
        ])
        
        # Add suppress tokens if specified (skip for Windows console compatibility)
        # Note: SUPPRESS_TOKENS with Unicode may cause display issues on Windows
        
        # Add initial prompt if specified
        if INITIAL_PROMPT:
            cmd.extend(["--initial_prompt", INITIAL_PROMPT])
            print(f"Using vocabulary-based initial prompt ({len(INITIAL_PROMPT)} chars)")
        
        print(f"\n========================================")
        print(f"Processing: {Path(video_path).name}")
        print(f"========================================")
        print(f"Running WhisperX (this may take several minutes)...")
        print(f"Command: {' '.join(cmd)}")
        print("\n[WhisperX Output]")
        
        try:
            # Run WhisperX with real-time output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Show real-time output
            for line in iter(process.stdout.readline, ''):
                print(line.rstrip())
            
            process.wait()
            
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd)
            
            # Find the generated JSON file
            json_path = Path(output_dir) / f"{video_name}.json"
            if not json_path.exists():
                raise FileNotFoundError(f"WhisperX did not generate expected JSON file: {json_path}")
            
            print(f"\nWhisperX completed!")
            print(f"Generated: {json_path}")
            
            return str(json_path)
            
        except subprocess.CalledProcessError as e:
            print(f"\nError: WhisperX failed with return code {e.returncode}")
            print(f"Command: {' '.join(cmd)}")
            print("\nPossible solutions:")
            print("1. Ensure WhisperX is installed: pip install whisperx")
            print("2. Activate virtual environment if needed: whisperx-env\\Scripts\\activate")
            print("3. Check that input file exists and is a valid video format")
            raise
        except FileNotFoundError as e:
            if "whisperx" in str(e):
                print(f"\nError: WhisperX command not found")
                print("Please install WhisperX: pip install whisperx")
                print("Or activate the virtual environment: whisperx-env\\Scripts\\activate")
            else:
                print(f"\nError: {e}")
            raise
        except Exception as e:
            print(f"\nUnexpected error running WhisperX: {e}")
            raise

    def process_video(self, video_path, output_dir="output"):
        """Complete pipeline: video → WhisperX → DaVinci SRT with auto-detected frame rate"""
        try:
            # Auto-detect frame rate if not already set
            if self.fps is None:
                print("Detecting video frame rate...")
                self.fps = get_video_fps(video_path)
                self._calculate_timing_values()
                print()  # Add spacing after timing values
            
            # Step 1: Run WhisperX
            json_path = self.run_whisperx(video_path, output_dir)
            
            # Step 2: Generate DaVinci-optimized SRT
            video_name = Path(video_path).stem
            output_srt = Path(output_dir) / f"{video_name}_davinci.srt"
            
            print(f"\nGenerating DaVinci-optimized subtitles...")
            self.process_file(json_path, str(output_srt))
            
            print(f"\n========================================")
            print(f"COMPLETED: {Path(video_path).name}")
            print(f"Output: {output_srt}")
            print(f"========================================")
            
            return str(output_srt)
            
        except Exception as e:
            print(f"\n========================================")
            print(f"FAILED: {Path(video_path).name}")
            print(f"Error: {e}")
            print(f"========================================")
            raise

    def process_input_folder(self, input_dir="input", output_dir="output"):
        """Process all videos in input folder."""
        # Create directories if they don't exist
        Path(input_dir).mkdir(parents=True, exist_ok=True)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Supported video formats
        video_extensions = ['*.mp4', '*.mov', '*.avi', '*.mkv', '*.webm', '*.m4v', '*.wmv', '*.flv', '*.3gp']
        
        # Find all video files (avoid duplicates by using set)
        video_files = set()
        for extension in video_extensions:
            video_files.update(glob.glob(str(Path(input_dir) / extension)))
            video_files.update(glob.glob(str(Path(input_dir) / extension.upper())))
        
        video_files = sorted(list(video_files))  # Convert to sorted list
        
        if not video_files:
            print(f"\n========================================")
            print(f"No video files found in: {input_dir}")
            print(f"========================================")
            print(f"Supported formats: {', '.join([ext.replace('*', '') for ext in video_extensions])}")
            print(f"\nTo add videos:")
            print(f"1. Place video files in the '{input_dir}' folder")
            print(f"2. Run this script again")
            print(f"\nTo process a single video:")
            print(f"python davinci_srt_generator.py --mode video --input your_video.mp4")
            return []
        
        print(f"\n========================================")
        print(f"Found {len(video_files)} video file(s) in: {input_dir}")
        print(f"========================================")
        for i, video in enumerate(video_files, 1):
            print(f"{i}. {Path(video).name}")
        print()
        
        # Process each video
        results = []
        successful = 0
        failed = 0
        
        for i, video_path in enumerate(video_files, 1):
            try:
                print(f"\n[{i}/{len(video_files)}] Processing: {Path(video_path).name}")
                output_srt = self.process_video(video_path, output_dir)
                results.append({
                    'video': video_path,
                    'srt': output_srt,
                    'status': 'success'
                })
                successful += 1
            except Exception as e:
                results.append({
                    'video': video_path,
                    'error': str(e),
                    'status': 'failed'
                })
                failed += 1
        
        # Final summary
        print(f"\n========================================")
        print(f"BATCH PROCESSING COMPLETE")
        print(f"========================================")
        print(f"Successful: {successful}/{len(video_files)}")
        print(f"Failed: {failed}/{len(video_files)}")
        
        if successful > 0:
            print(f"\nGenerated SRT files:")
            for result in results:
                if result['status'] == 'success':
                    video_name = Path(result['video']).name
                    srt_name = Path(result['srt']).name
                    print(f"  [OK] {video_name} -> {srt_name}")
        
        if failed > 0:
            print(f"\nFailed files:")
            for result in results:
                if result['status'] == 'failed':
                    video_name = Path(result['video']).name
                    print(f"  [FAILED] {video_name}: {result['error']}")
        
        return results

    # Include all the original processing methods...
    def ms_to_frame_boundary(self, ms):
        """Convert milliseconds to exact frame boundary."""
        frame_number = round(ms / self.frame_duration_ms)
        return frame_number * self.frame_duration_ms
    
    def ms_to_next_frame_boundary(self, ms):
        """Convert milliseconds to next frame boundary (always rounds up)."""
        import math
        frame_number = math.ceil(ms / self.frame_duration_ms)
        return frame_number * self.frame_duration_ms

    def seconds_to_frame_boundary(self, seconds):
        """Convert seconds to frame-aligned milliseconds."""
        ms = seconds * 1000.0
        return self.ms_to_frame_boundary(ms)

    def ms_to_timedelta(self, ms):
        """Convert milliseconds to timedelta."""
        return timedelta(milliseconds=ms)
    
    def apply_gap_based_rules(self, current_group, next_group, gap_ms):
        """Apply phrase boundary detection with gap-based timing rules."""
        TOLERANCE_MS = 1.0                # ±1ms tolerance for frame boundary detection
        
        next_group_start_ms = next_group["start_ms"]
        current_group_end_ms = current_group["end_ms"]
        
        if abs(gap_ms - self.phrase_gap_threshold_ms) <= TOLERANCE_MS:
            # Gap ≈ 5 frames = phrase boundary with clean gap
            adjusted_end = next_group_start_ms - self.extension_ms
            return adjusted_end
            
        elif gap_ms > self.phrase_gap_threshold_ms:
            # Gap > 5 frames = phrase boundary
            adjusted_end = current_group_end_ms + self.extension_ms
            return adjusted_end
            
        else:
            # Gap < 5 frames = within phrase = continuous speech flow
            return None

    def process_whisperx_json(self, json_path):
        """Extract word timings from WhisperX JSON."""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Flatten all words from all segments
        words = []
        for segment in data.get("segments", []):
            for word in segment.get("words", []):
                if all(key in word for key in ("start", "end", "word")):
                    words.append({
                        "text": word["word"].strip(),
                        "start_ms": word["start"] * 1000.0,
                        "end_ms": word["end"] * 1000.0
                    })
        
        print(f"Extracted {len(words)} words from WhisperX JSON")
        return words

    def group_words(self, words):
        """Group words into 1-2 word phrases based on natural speech patterns."""
        if not words:
            return []
        
        # Duration threshold for emphasized words (in milliseconds) - dynamic based on frame rate
        # Now calculated from self.emphasis_duration_ms (6 frames worth)
        
        # Prepositions that should group with following word
        PREPOSITIONS = {'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'into', 'over', 'under'}
        
        # Articles that should group with following word
        ARTICLES = {'a', 'an', 'the'}
        
        # Common phrase patterns that should stay together
        KEEP_TOGETHER_PHRASES = {
            ('bit', 'of'), ('kind', 'of'), ('sort', 'of'), ('lot', 'of'),
            ('out', 'of'), ('instead', 'of'), ('because', 'of'),
            ('up', 'to'), ('used', 'to'), ('have', 'to'), ('want', 'to'),
            ('going', 'to'), ('trying', 'to'), ('need', 'to'),
            ('a', 'little'), ('a', 'bit'), ('the', 'way'),
            ('in', 'order'), ('at', 'all'), ('of', 'course'),
        }
        
        # Important words that should often stand alone when capitalized
        IMPORTANT_SOLO_WORDS = {'Time', 'Jail', 'Prison', 'Court', 'Judge', 'Police'}
        
        groups = []
        i = 0
        
        while i < len(words):
            current_word = words[i]
            current_text = current_word["text"]
            
            # Check if we can group with next word
            can_group = False
            if i + 1 < len(words):
                next_word = words[i + 1]
                next_text = next_word["text"]
                
                # Calculate word durations
                current_duration = current_word["end_ms"] - current_word["start_ms"]
                next_duration = next_word["end_ms"] - next_word["start_ms"]
                
                # Clean text for comparisons
                current_clean = current_text.rstrip('.!?;:,—–-')
                next_clean = next_text.rstrip('.!?;:,—–-')
                
                # Check various conditions
                ends_with_punctuation = current_text and current_text[-1] in '.!?;:,—–-'
                is_common_phrase = (current_clean.lower(), next_clean.lower()) in KEEP_TOGETHER_PHRASES
                current_is_important = current_clean in IMPORTANT_SOLO_WORDS
                current_is_preposition = current_clean.lower() in PREPOSITIONS
                current_is_article = current_clean.lower() in ARTICLES
                
                # Check if either word is emphasized
                if current_is_preposition or current_is_article:
                    current_emphasized = current_duration > self.emphasis_duration_ms * 2  # Double threshold
                    next_emphasized = next_duration > self.emphasis_duration_ms * 2
                else:
                    current_emphasized = current_duration > self.emphasis_duration_ms
                    next_emphasized = next_duration > self.emphasis_duration_ms
                
                next_is_capitalized = (next_text and next_text[0].isupper() and 
                                     i > 0 and next_clean not in ['I'])
                
                current_short = len(current_clean) < 7
                next_short = len(next_clean) < 7
                gap_ms = next_word["start_ms"] - current_word["end_ms"]
                
                # PRIORITY GROUPING LOGIC
                if ends_with_punctuation:
                    can_group = False
                elif current_is_preposition or current_is_article:
                    if gap_ms < 1000 and not next_emphasized:
                        can_group = True
                elif is_common_phrase:
                    can_group = True
                elif current_is_important:
                    can_group = False
                elif current_emphasized or next_emphasized:
                    can_group = False
                elif gap_ms > self.max_gap_ms:
                    can_group = False
                elif next_is_capitalized:
                    can_group = False
                elif current_short and next_short:
                    can_group = True
                else:
                    can_group = False
            
            if can_group:
                # Create two-word group with configurable separator
                combined_text = f"{current_text}{self.SEPARATOR}{next_text}"
                
                group = {
                    "text": combined_text,
                    "start_ms": current_word["start_ms"],
                    "end_ms": next_word["end_ms"],
                    "original_start": current_word["start_ms"],
                    "original_end": next_word["end_ms"],
                    "word_count": 2
                }
                groups.append(group)
                i += 2  # Skip next word since we grouped it
            else:
                # Create single-word group
                group = {
                    "text": current_text,
                    "start_ms": current_word["start_ms"],
                    "end_ms": current_word["end_ms"],
                    "original_start": current_word["start_ms"],
                    "original_end": current_word["end_ms"],
                    "word_count": 1
                }
                groups.append(group)
                i += 1  # Move to next word
        
        # Count grouping method used
        two_word_groups = sum(1 for group in groups if group["word_count"] == 2)
        one_word_groups = sum(1 for group in groups if group["word_count"] == 1)
        
        print(f"Grouped {len(words)} words into {len(groups)} subtitles")
        print(f"  Two-word groups: {two_word_groups} (using regular spaces)")
        print(f"  Single words: {one_word_groups}")
        
        return groups

    def create_seamless_timings(self, groups):
        """Core logic to adjust timings with overlaps for DaVinci Resolve."""
        if not groups:
            return []

        processed_groups = []
        
        for i, group in enumerate(groups):
            # Start with frame-aligned original timing
            start_ms = self.seconds_to_frame_boundary(group["start_ms"] / 1000.0)
            end_ms = self.seconds_to_frame_boundary(group["end_ms"] / 1000.0)
            
            # Ensure minimum duration
            if end_ms - start_ms < self.min_duration_ms:
                end_ms = start_ms + self.min_duration_ms
            
            # Handle timing with next group
            gap_based_end_ms = None
            gap_ms = 0
            
            if i + 1 < len(groups):
                next_group = groups[i + 1]
                next_start_ms = self.seconds_to_frame_boundary(next_group["start_ms"] / 1000.0)
                
                # Calculate gap between ORIGINAL timings
                original_end_ms = group["end_ms"]
                original_next_start_ms = next_group["start_ms"]
                gap_ms = original_next_start_ms - original_end_ms
                
                # Apply gap-based rules FIRST
                gap_based_end_ms = self.apply_gap_based_rules(group, next_group, gap_ms)
                
                if gap_based_end_ms is not None:
                    end_ms = self.ms_to_frame_boundary(gap_based_end_ms)
                elif gap_ms <= self.max_gap_ms:  # Use existing overlap logic
                    overlap_end_ms = next_start_ms + self.overlap_ms
                    end_ms = self.ms_to_next_frame_boundary(overlap_end_ms)
                    
                    # Ensure we don't create unreasonably long subtitle
                    if end_ms - start_ms > 3000:  # 3 second max
                        end_ms = start_ms + 3000
                else:
                    # Very large gap: keep original timing but frame-align
                    end_ms = self.seconds_to_frame_boundary(group["end_ms"] / 1000.0)
            else:
                # Last group: frame-align the original end time
                end_ms = self.seconds_to_frame_boundary(group["end_ms"] / 1000.0)
            
            # Track timing strategy
            if i + 1 < len(groups):
                if gap_based_end_ms is not None:
                    timing_strategy = "phrase_boundary"
                else:
                    timing_strategy = "seamless_overlap"
            else:
                timing_strategy = "last_group"
            
            processed_groups.append({
                "text": group["text"],
                "start_ms": start_ms,
                "end_ms": end_ms,
                "original_start": group["original_start"],
                "original_end": group["original_end"],
                "word_count": group["word_count"],
                "timing_strategy": timing_strategy,
                "original_gap": gap_ms if i + 1 < len(groups) else None
            })
        
        return processed_groups

    def generate_srt(self, groups, output_path):
        """Write properly formatted SRT file with placeholder if dialogue doesn't start at 0:00."""
        srt_subtitles = []
        subtitle_index = 1
        
        # Check if we need a placeholder subtitle at the beginning
        if groups and groups[0]["start_ms"] > 0:
            # Create placeholder subtitle from 0:00 to start of first subtitle
            placeholder_end_ms = groups[0]["start_ms"] - self.overlap_ms
            
            # Ensure placeholder has minimum duration
            if placeholder_end_ms < self.min_duration_ms:
                placeholder_end_ms = self.min_duration_ms
                
            # Frame-align the placeholder end time
            placeholder_end_ms = self.ms_to_frame_boundary(placeholder_end_ms)
            
            placeholder = srt.Subtitle(
                index=subtitle_index,
                start=self.ms_to_timedelta(0),
                end=self.ms_to_timedelta(placeholder_end_ms),
                content="delete me",
                proprietary=''
            )
            srt_subtitles.append(placeholder)
            subtitle_index += 1
            
            print(f"Added placeholder subtitle: 0:00 -> {placeholder_end_ms/1000:.3f}s")
        
        # Add all regular subtitles
        for group in groups:
            subtitle = srt.Subtitle(
                index=subtitle_index,
                start=self.ms_to_timedelta(group["start_ms"]),
                end=self.ms_to_timedelta(group["end_ms"]),
                content=group["text"],
                proprietary=''
            )
            srt_subtitles.append(subtitle)
            subtitle_index += 1
        
        # Write SRT file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(srt.compose(srt_subtitles))
        
        print(f"\nGenerated SRT file: {output_path}")
        print(f"Total subtitles: {len(srt_subtitles)}")
        
        # Statistics
        overlaps = sum(1 for i in range(len(groups)-1) 
                      if groups[i]["end_ms"] > groups[i+1]["start_ms"])
        
        if len(groups) > 1:
            print(f"Overlapping subtitles: {overlaps}/{len(groups)-1} ({overlaps/(len(groups)-1)*100:.1f}%)")

    def process_file(self, json_path, output_path):
        """Main processing function."""
        print(f"Processing: {json_path}")
        
        # Extract words from WhisperX JSON
        words = self.process_whisperx_json(json_path)
        
        if not words:
            print("No words found in input file!")
            return
        
        # Group words into phrases
        groups = self.group_words(words)
        
        # Apply DaVinci-specific timing adjustments
        processed_groups = self.create_seamless_timings(groups)
        
        # Generate SRT file
        self.generate_srt(processed_groups, output_path)
        
        print(f"\n[SUCCESS] Generated DaVinci Resolve compatible SRT:")
        print(f"  Input:  {json_path}")
        print(f"  Output: {output_path}")


def main():
    """Main function with argument parsing for multiple modes."""
    parser = argparse.ArgumentParser(
        description="DaVinci Resolve SRT Generator with WhisperX Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all videos in input folder (auto-detect frame rate)
  python davinci_srt_generator.py
  
  # Process single video file (auto-detect frame rate)
  python davinci_srt_generator.py --mode video --input movie.mp4
  
  # Process existing JSON file (original functionality)
  python davinci_srt_generator.py --mode json --input output/movie.json
  
  # Override frame rate for specific video
  python davinci_srt_generator.py --mode video --input movie.mp4 --fps 60
  
  # Custom directories with frame rate override
  python davinci_srt_generator.py --input my_videos --output my_srt_files --fps 29.97
        """
    )
    
    parser.add_argument('--mode', 
                       choices=['json', 'video', 'folder'], 
                       default='folder',
                       help='Processing mode: json (existing), video (single), folder (batch)')
    parser.add_argument('--input', 
                       help='Input file/folder path (default: input/ for folder mode, required for others)')
    parser.add_argument('--output', 
                       default='output', 
                       help='Output directory (default: output)')
    parser.add_argument('--fps', 
                       type=float, 
                       help='Override video frame rate (auto-detect if not specified)')
    
    args = parser.parse_args()
    
    # Create generator instance with fps if provided, otherwise None for auto-detect
    generator = DaVinciSRTGenerator(fps=args.fps)
    
    try:
        if args.mode == 'json':
            # Original JSON processing functionality
            if not args.input:
                print("Error: --input required for JSON mode")
                print("Example: python davinci_srt_generator.py --mode json --input output/movie.json")
                sys.exit(1)
            
            input_file = args.input
            output_file = str(Path(args.output) / f"{Path(input_file).stem}_davinci.srt")
            
            print(f"\n========================================")
            print(f"JSON MODE: Processing existing WhisperX JSON")
            print(f"========================================")
            
            generator.process_file(input_file, output_file)
            
        elif args.mode == 'video':
            # Single video processing
            if not args.input:
                print("Error: --input required for video mode")
                print("Example: python davinci_srt_generator.py --mode video --input movie.mp4")
                sys.exit(1)
            
            if not Path(args.input).exists():
                print(f"Error: Video file not found: {args.input}")
                sys.exit(1)
            
            print(f"\n========================================")
            print(f"VIDEO MODE: Complete pipeline (video → WhisperX → SRT)")
            print(f"========================================")
            
            generator.process_video(args.input, args.output)
            
        elif args.mode == 'folder':
            # Batch folder processing (default)
            input_dir = args.input or 'input'
            
            print(f"\n========================================")
            print(f"FOLDER MODE: Batch processing all videos")
            print(f"========================================")
            print(f"Input directory: {input_dir}")
            print(f"Output directory: {args.output}")
            
            generator.process_input_folder(input_dir, args.output)
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\nError: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()