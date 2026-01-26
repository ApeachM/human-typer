# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Human Typer is a PyQt5-based tool that simulates human-like typing with realistic delays, typos, and natural speed variations. It supports both GUI and CLI modes, with special features for automation (watch mode) and window management.

## Key Commands

### Running the Application

```bash
# GUI mode (default)
python human_typer.py
# or
python -m human_typer

# CLI mode
python human_typer.py -f input.txt
python human_typer.py -t "text to type"
echo "text" | python human_typer.py --stdin

# Watch mode (for automation/Claude integration)
python human_typer.py --watch
python human_typer.py --watch --delete --window "VS Code"

# List available windows
python human_typer.py --list-windows
```

### Development Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run via convenience scripts
./run_human_typer.sh       # Linux/macOS
run_human_typer.bat        # Windows
```

### Testing

There are no automated tests in this repository. Manual testing should focus on:
- GUI functionality (start/stop/resume, window detection)
- CLI modes (file, stdin, watch)
- Human-like typing features (delays, typos, rhythm)
- Cross-platform window management (Linux xprop/wmctrl, Windows/macOS pyautogui)

## Architecture

### Module Structure

The codebase follows a clean package structure under `human_typer/`:

- **`config.py`**: Central configuration using dataclass pattern. Contains all timing constants, character modifiers, typo settings, and adjacent key mappings for realistic typing simulation
- **`typing_thread.py`**: Core typing engine (`TypingThread` class). Runs in a QThread background thread and implements all human-like behaviors:
  - Exponential delay distribution (not uniform)
  - Character-specific delays (punctuation slower, repeated chars faster)
  - Typing rhythm that drifts over time (0.6x to 1.8x)
  - Typo simulation with streak probability (consecutive typos are more likely)
  - Buffered typo correction (types wrong chars, pauses, backspaces all, retypes correct)
- **`main_window.py`**: PyQt5 GUI (`HumanTyper` class). Features:
  - Active window detection via timer (every 300ms)
  - Window targeting with "Fix" mode to lock target
  - Cross-platform window activation (Linux uses xprop/wmctrl/xdotool, others use pyautogui)
  - Pause/resume support with position tracking
- **`cli.py`**: Command-line interface with argument parsing. Includes watch mode that monitors a file path and auto-types when file appears
- **`__main__.py`**: GUI entry point
- **`__init__.py`**: Package exports

### Key Design Patterns

**Threading Model**: GUI uses QThread for background typing to keep UI responsive. The thread emits signals for progress updates and completion.

**Typo Simulation**: Uses QWERTY keyboard adjacency mapping in `config.py`. Typos are buffered and corrected together (realistic "oh wait, backspace backspace backspace" behavior).

**Window Management**: Platform-specific implementations with graceful fallbacks:
- Linux: subprocess calls to xprop → wmctrl → xdotool
- Windows/macOS: pyautogui window methods

**Typing Algorithm**: Three-layer delay calculation:
1. Base delay: `random.expovariate(3.0 / delay_range)` clamped to [min, max]
2. Character modifier: based on char type (e.g., 1.8x for punctuation)
3. Rhythm multiplier: drifts randomly between 0.6x and 1.8x over time

**Watch Mode**: Designed for Claude/automation. Polls file path every 500ms. When file exists with content, activates target window (if specified), types content, optionally deletes file.

## Important Implementation Details

### Human-Like Typing Features

All timing/behavior constants are in `config.py`. Key modifiers:
- Punctuation: 1.8x slower
- Special chars: 2.0x slower
- Capital letters: 1.4x slower (shift overhead)
- Repeated chars: 0.6x faster (finger already positioned)
- Common letters (top 10): 0.85x faster (muscle memory)
- Newlines: 4.0x slower (thinking pause)

Typo system:
- Base probability: 2% per alphanumeric char
- After typo: 35% chance of another typo (streak)
- Streak decays by 0.6x each non-typo char
- Correction delay: 150ms pause before backspacing

### Cross-Platform Considerations

**Linux Window Management**: Requires xprop (usually installed). wmctrl or xdotool needed for CLI window activation but optional for GUI.

**Non-ASCII Characters**: Uses clipboard + Ctrl+V for Korean and other non-ASCII (pyautogui.write() only handles ASCII).

**pyautogui Configuration**: FAILSAFE enabled (move mouse to corner to abort). PAUSE set to 0 for precise timing control.

### Watch Mode for Claude Integration

Default watch path: `~/.human_typer_input.txt`

Claude should write to this file:
```bash
cat > ~/.human_typer_input.txt << 'EOF'
# content here
EOF
```

User runs: `python human_typer.py --watch --delete --window "Code"`

This enables fully automated typing from Claude to specific applications.

## Code Style Notes

- Type hints used throughout (Python 3.10+ syntax with `|` for unions)
- PyQt5 signal/slot pattern for thread communication
- Dataclass for configuration (immutable singleton)
- Platform detection with graceful fallbacks
- No external logging framework (print to stderr for errors)
