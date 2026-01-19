#!/bin/bash
#
# Human-like Typing Tool Launcher
# Automatically sets up virtual environment and runs the tool
# Requires Python 3.10 or higher
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv_human_typer"
PYTHON_SCRIPT="$SCRIPT_DIR/human_typer.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Human-like Typing Tool ===${NC}"

# Find Python 3.10+ (prefer newer versions)
PYTHON_BIN=""

if command -v python3.12 &> /dev/null; then
    PYTHON_BIN="python3.12"
elif command -v python3.11 &> /dev/null; then
    PYTHON_BIN="python3.11"
elif command -v python3.10 &> /dev/null; then
    PYTHON_BIN="python3.10"
elif command -v python3 &> /dev/null; then
    # Check if python3 is 3.10+
    PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
    if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 10 ]; then
        PYTHON_BIN="python3"
    fi
fi

# Check if suitable Python was found
if [ -z "$PYTHON_BIN" ]; then
    echo -e "${RED}Error: Python 3.10 or higher is required${NC}"
    echo ""
    echo "Please install Python 3.10+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3.10"
    echo "  RHEL/CentOS:   sudo dnf install python3.10"
    echo "  Fedora:        sudo dnf install python3.10"
    exit 1
fi

echo -e "${GREEN}Using: $($PYTHON_BIN --version)${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    $PYTHON_BIN -m venv "$VENV_DIR"

    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created${NC}"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Check and install dependencies
DEPS_INSTALLED=true

python3 -c "import PyQt5" 2>/dev/null || DEPS_INSTALLED=false
python3 -c "import pyautogui" 2>/dev/null || DEPS_INSTALLED=false
python3 -c "import pyperclip" 2>/dev/null || DEPS_INSTALLED=false

if [ "$DEPS_INSTALLED" = false ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install --upgrade pip -q
    pip install PyQt5 pyautogui pyperclip -q

    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to install dependencies${NC}"
        deactivate
        exit 1
    fi
    echo -e "${GREEN}Dependencies installed${NC}"
fi

# Run the tool
echo -e "${GREEN}Starting Human-like Typing Tool...${NC}"
echo ""
python3 "$PYTHON_SCRIPT"

# Deactivate virtual environment on exit
deactivate
