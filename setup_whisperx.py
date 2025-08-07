"""
WhisperX Setup Script
Handles platform-specific installation of dependencies
"""

import subprocess
import sys
import platform
import os
import argparse

def check_python_version() -> bool:
    """Ensure Python 3.10 or 3.11 is being used."""
    version = sys.version_info
    if version.major != 3 or version.minor < 10 or version.minor > 11:
        print(f"[ERROR] Unsupported Python version detected: {version.major}.{version.minor}")
        print("        Please use Python 3.10 or 3.11")
        print("        Download from: https://www.python.org/downloads/")
        return False
    print(f"[OK] Python {version.major}.{version.minor} detected")
    return True

def check_ffmpeg() -> bool:
    """Check if ffmpeg is installed."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("[OK] ffmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[X] ffmpeg not found")
        print("   Windows: winget install ffmpeg")
        print("   Or download from: https://www.gyan.dev/ffmpeg/builds/")
        return False

def check_git():
    """Check if git is installed."""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        print("[OK] Git is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[X] Git not found")
        print("   Download from: https://git-scm.com/download/win")
        return False

def detect_gpu() -> bool:
    """Detect if an NVIDIA CUDA GPU is likely available using nvidia-smi if present."""
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True)
        if result.returncode == 0:
            print("[OK] NVIDIA GPU detected (nvidia-smi present)")
            return True
    except FileNotFoundError:
        pass
    print("[INFO] No NVIDIA GPU detected - will install CPU PyTorch")
    return False

def install_pytorch():
    """Install appropriate PyTorch version based on GPU detection."""
    print("\n[INSTALL] Installing PyTorch...")
    has_gpu = detect_gpu()
    if has_gpu:
        print("   Installing CUDA-enabled PyTorch (cu118)")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "torch", "torchvision", "torchaudio",
            "--index-url", "https://download.pytorch.org/whl/cu118"
        ])
    else:
        print("   Installing CPU-only PyTorch")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "torch", "torchvision", "torchaudio",
            "--index-url", "https://download.pytorch.org/whl/cpu"
        ])

def install_requirements():
    """Install requirements.txt."""
    print("\n[INSTALL] Installing WhisperX and dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
def main():
    parser = argparse.ArgumentParser(description="WhisperX Setup Script")
    parser.add_argument("--yes", "-y", action="store_true", help="Run non-interactively and continue past optional prompts")
    args = parser.parse_args()

    print("=" * 50)
    print("WhisperX Setup Script")
    print("=" * 50)

    # Check prerequisites
    print("\n[CHECK] Checking prerequisites...")
    if not check_python_version():
        sys.exit(1)

    if not check_git():
        sys.exit(1)

    if not check_ffmpeg():
        print("   [WARNING] ffmpeg is required for video processing")
        if not args.yes:
            response = input("   Continue anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(1)

    # Upgrade pip
    print("\n[INSTALL] Upgrading pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

    # Install PyTorch
    install_pytorch()

    # Install requirements
    install_requirements()

    # Verify installation
    print("\n[VERIFY] Verifying installation...")
    try:
        import whisperx  # type: ignore
        print("[OK] WhisperX installed successfully")
    except ImportError:
        print("[X] WhisperX installation failed")
        sys.exit(1)

    try:
        import srt  # type: ignore
        print("[OK] SRT module installed successfully")
    except ImportError:
        print("[X] SRT module installation failed")
        sys.exit(1)

    # Report GPU availability
    detect_gpu()

    print("\n" + "=" * 50)
    print("[OK] Setup complete!")
    print("=" * 50)
    print("\nYou can now run:")
    print("  python davinci_srt_generator.py")
    
if __name__ == "__main__":
    main()