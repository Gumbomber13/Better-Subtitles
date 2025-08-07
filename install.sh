#!/bin/bash
set -e

echo "========================================"
echo "WhisperX One-Click Installer"
echo "========================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_ok() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        print_error "Python not found!"
        echo "Please install Python 3.10 or 3.11:"
        echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
        echo "  macOS: brew install python@3.11"
        echo "  Or download from: https://www.python.org/downloads/"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
print_ok "Found Python $PYTHON_VERSION"

# Check if Git is installed
if ! command -v git &> /dev/null; then
    print_error "Git not found!"
    echo "Please install Git:"
    echo "  Ubuntu/Debian: sudo apt install git"
    echo "  macOS: brew install git"
    echo "  Or download from: https://git-scm.com/downloads"
    exit 1
fi
print_ok "Git is installed"

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    print_warning "ffmpeg not found!"
    echo "This is required for video processing."
    echo "Install with:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo
    read -p "Continue without ffmpeg? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 1
    fi
else
    print_ok "ffmpeg is installed"
fi

echo
echo "========================================"
echo "Starting automated setup..."
echo "========================================"
echo

# Create virtual environment if missing
if [ ! -d "whisperx-env" ]; then
  echo "[INFO] Creating virtual environment in whisperx-env"
  $PYTHON_CMD -m venv whisperx-env
fi

# Activate the virtual environment
if [ -f "whisperx-env/bin/activate" ]; then
  # shellcheck disable=SC1091
  . whisperx-env/bin/activate
  PYTHON_CMD="python"
else
  print_warning "Could not activate virtual environment; continuing with system Python"
fi

# Run the Python setup script non-interactively and auto-run the generator
$PYTHON_CMD setup_whisperx.py --yes --run

if [ $? -ne 0 ]; then
    echo
    echo "========================================"
    print_error "Setup failed!"
    echo "========================================"
    echo
    echo "Try manual installation:"
    echo "1. See INSTALL_MANUAL.md for step-by-step instructions"
    echo "2. Or check the setup log above for specific errors"
    echo
    exit 1
fi

echo
echo "========================================"
print_ok "Installation Complete!"
echo "========================================"
echo
echo "You can now run:"
echo "  source whisperx-env/bin/activate"
echo "  $PYTHON_CMD davinci_srt_generator.py"
echo
echo "Or process videos in the 'input' folder automatically."
echo