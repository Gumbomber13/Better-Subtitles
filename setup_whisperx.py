"""
WhisperX Setup Script
Handles platform-specific installation of dependencies
"""

import subprocess
import sys
import platform
import os

def check_python_version():
    """Ensure Python 3.10 or 3.11 is being used."""
    version = sys.version_info
    if version.major != 3 or version.minor < 10 or version.minor > 11:
        print(f"[X] Python {version.major}.{version.minor} detected")
        print("[OK] Please use Python 3.10 or 3.11")
        print("   Download from: https://www.python.org/downloads/")
        return False
    print(f"[OK] Python {version.major}.{version.minor} detected")
    return True

def check_ffmpeg():
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

def detect_gpu():
    """Detect if CUDA GPU is available."""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"[OK] CUDA GPU detected: {torch.cuda.get_device_name(0)}")
            return True
    except ImportError:
        pass
    print("[INFO] No CUDA GPU detected - will use CPU")
    return False

def install_pytorch():
    """Install appropriate PyTorch version."""
    print("\n[INSTALL] Installing PyTorch...")
    
    # Try to detect if GPU is available
    has_gpu = False
    try:
        # Check for NVIDIA GPU on Windows
        if platform.system() == "Windows":
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
            if result.returncode == 0:
                has_gpu = True
                print("   NVIDIA GPU detected - installing CUDA version")
    except:
        pass
    
    if has_gpu:
        # Install GPU version
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "torch", "torchvision", "torchaudio",
            "--index-url", "https://download.pytorch.org/whl/cu118"
        ])
    else:
        # Install CPU version
        print("   Installing CPU version of PyTorch")
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
    print("="*50)
    print("WhisperX Setup Script")
    print("="*50)
    
    # Check prerequisites
    print("\n[CHECK] Checking prerequisites...")
    if not check_python_version():
        sys.exit(1)
    
    if not check_git():
        sys.exit(1)
    
    if not check_ffmpeg():
        print("   [WARNING] ffmpeg is required for video processing")
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
        import whisperx
        print("[OK] WhisperX installed successfully")
    except ImportError:
        print("[X] WhisperX installation failed")
        sys.exit(1)
    
    try:
        import srt
        print("[OK] SRT module installed successfully")
    except ImportError:
        print("[X] SRT module installation failed")
        sys.exit(1)
    
    # Test GPU
    detect_gpu()
    
    print("\n" + "="*50)
    print("[OK] Setup complete!")
    print("="*50)
    print("\nYou can now run:")
    print("  python davinci_srt_generator.py")
    
if __name__ == "__main__":
    main()