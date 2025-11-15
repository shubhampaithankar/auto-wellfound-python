#!/bin/bash
# Installation script for Linux and macOS
# This script installs Chrome, sets up a virtual environment, and installs dependencies

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Change to project root (parent directory of scripts folder)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "========================================="
echo "Wellfound Automation - Installation Script"
echo "========================================="
echo "Working directory: $(pwd)"
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "Detected OS: $MACHINE"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check and install Chrome/Chromium
echo "Step 1: Checking for Chrome/Chromium..."
if command_exists google-chrome || command_exists chromium-browser || command_exists chromium; then
    echo "✓ Chrome/Chromium is already installed"
    if command_exists google-chrome; then
        CHROME_CMD="google-chrome"
    elif command_exists chromium-browser; then
        CHROME_CMD="chromium-browser"
    else
        CHROME_CMD="chromium"
    fi
    echo "  Found: $CHROME_CMD"
elif [ "$MACHINE" = "Linux" ]; then
    echo "Chrome/Chromium not found. Installing Chromium..."
    if command_exists apt-get; then
        # Debian/Ubuntu
        sudo apt-get update
        sudo apt-get install -y chromium-browser
        CHROME_CMD="chromium-browser"
    elif command_exists yum; then
        # CentOS/RHEL
        sudo yum install -y chromium
        CHROME_CMD="chromium"
    elif command_exists dnf; then
        # Fedora
        sudo dnf install -y chromium
        CHROME_CMD="chromium"
    elif command_exists pacman; then
        # Arch Linux
        sudo pacman -S --noconfirm chromium
        CHROME_CMD="chromium"
    else
        echo "⚠ Could not detect package manager. Please install Chrome/Chromium manually:"
        echo "  - Ubuntu/Debian: sudo apt-get install chromium-browser"
        echo "  - Fedora: sudo dnf install chromium"
        echo "  - Arch: sudo pacman -S chromium"
        echo "  - Or download from: https://www.google.com/chrome/"
        read -p "Press Enter to continue after installing Chrome..."
    fi
elif [ "$MACHINE" = "Mac" ]; then
    echo "Chrome not found. Checking if Homebrew is available..."
    if command_exists brew; then
        echo "Installing Chrome via Homebrew..."
        brew install --cask google-chrome
        CHROME_CMD="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    else
        echo "⚠ Homebrew not found. Please install Chrome manually:"
        echo "  1. Download from: https://www.google.com/chrome/"
        echo "  2. Or install Homebrew first: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        read -p "Press Enter to continue after installing Chrome..."
    fi
fi
echo ""

# Check for Python
echo "Step 2: Checking for Python..."
if ! command_exists python3; then
    echo "❌ Python 3 is not installed!"
    if [ "$MACHINE" = "Linux" ]; then
        echo "Please install Python 3:"
        echo "  - Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
        echo "  - Fedora: sudo dnf install python3 python3-pip"
        echo "  - Arch: sudo pacman -S python python-pip"
    elif [ "$MACHINE" = "Mac" ]; then
        echo "Please install Python 3:"
        echo "  - Install from: https://www.python.org/downloads/"
        echo "  - Or use Homebrew: brew install python3"
    fi
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✓ Found: $PYTHON_VERSION"
echo ""

# Check for pip
echo "Step 3: Checking for pip..."
if ! command_exists pip3; then
    echo "⚠ pip3 not found. Installing pip..."
    if [ "$MACHINE" = "Linux" ]; then
        sudo apt-get install -y python3-pip || sudo yum install -y python3-pip || sudo dnf install -y python3-pip
    elif [ "$MACHINE" = "Mac" ]; then
        python3 -m ensurepip --upgrade
    fi
fi
echo "✓ pip is available"
echo ""

# Create virtual environment
echo "Step 4: Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠ Virtual environment 'venv' already exists"
    read -p "Do you want to remove it and create a new one? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "✓ Created new virtual environment"
    else
        echo "✓ Using existing virtual environment"
    fi
else
    python3 -m venv venv
    echo "✓ Created virtual environment"
fi
echo ""

# Activate virtual environment and install requirements
echo "Step 5: Installing Python dependencies..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing packages from requirements.txt..."
    pip install -r requirements.txt
    echo "✓ All dependencies installed"
else
    echo "⚠ requirements.txt not found!"
    exit 1
fi
echo ""

# Create .env file if it doesn't exist
echo "Step 6: Setting up environment file..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ Created .env file from .env.example"
        echo "⚠ Please edit .env file with your credentials before running the script"
    else
        echo "⚠ .env.example not found. Please create .env file manually"
    fi
else
    echo "✓ .env file already exists"
fi
echo ""

echo "========================================="
echo "Installation Complete! 🎉"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials:"
echo "   - WELLFOUND_EMAIL"
echo "   - WELLFOUND_PASSWORD"
echo "   - RESEND_API_KEY (optional, for email reports)"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the script:"
echo "   python -u main.py"
echo "   or"
echo "   ./run.sh"
echo ""

