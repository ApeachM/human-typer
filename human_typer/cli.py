"""Command-line interface for Human Typer."""

import argparse
import sys
import time
import os
import random

import pyautogui
import pyperclip
from pynput.keyboard import Controller, Key

from .config import config

# Configure pyautogui (still used for window detection)
pyautogui.FAILSAFE = config.FAILSAFE_ENABLED
pyautogui.PAUSE = config.PAUSE_BETWEEN_ACTIONS

# pynput keyboard controller for precise key control
keyboard = Controller()

# Default watch file path
DEFAULT_WATCH_FILE = os.path.expanduser("~/.human_typer_input.txt")


def is_ascii(char: str) -> bool:
    """Check if character is ASCII."""
    return ord(char) < 128


def type_char(char: str) -> None:
    """Type a single character using pynput for precise control."""
    if char == '\n':
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        return
    elif char == '\t':
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        return
    elif not is_ascii(char):
        # Non-ASCII: use clipboard
        pyperclip.copy(char)
        keyboard.press(Key.ctrl_l)
        keyboard.press('v')
        keyboard.release('v')
        keyboard.release(Key.ctrl_l)
        return

    # ASCII character - pynput provides precise timing control
    # Map special characters to their base key + shift
    shift_chars = {
        '!': '1', '@': '2', '#': '3', '$': '4', '%': '5',
        '^': '6', '&': '7', '*': '8', '(': '9', ')': '0',
        '_': '-', '+': '=', '{': '[', '}': ']', '|': '\\',
        ':': ';', '"': "'", '<': ',', '>': '.', '?': '/',
        '~': '`'
    }

    if char.isupper():
        # Capital letter - HTML5 RDP/VNC needs significant delay
        keyboard.press(Key.shift)
        time.sleep(0.1)  # HTML5 remote desktop needs extra time
        keyboard.press(char.lower())
        time.sleep(0.1)
        keyboard.release(char.lower())
        time.sleep(0.1)
        keyboard.release(Key.shift)
        time.sleep(0.1)  # Stabilization delay
    elif char in shift_chars:
        # Special character - HTML5 RDP/VNC needs significant delay
        keyboard.press(Key.shift)
        time.sleep(0.1)  # HTML5 remote desktop needs extra time
        keyboard.press(shift_chars[char])
        time.sleep(0.1)
        keyboard.release(shift_chars[char])
        time.sleep(0.1)
        keyboard.release(Key.shift)
        time.sleep(0.1)  # Stabilization delay
    else:
        # Normal character (lowercase, digit, space, etc.)
        keyboard.press(char)
        time.sleep(0.1)
        keyboard.release(char)


def get_base_delay(min_delay: float, max_delay: float) -> float:
    """Get base delay using exponential distribution."""
    delay_range = max_delay - min_delay
    if delay_range <= 0:
        return min_delay

    extra_delay = random.expovariate(3.0 / delay_range)
    return min(min_delay + extra_delay, max_delay)


def get_char_modifier(char: str, prev_char: str) -> float:
    """Get delay modifier based on character type."""
    # Repeated character - faster
    if char.lower() == prev_char.lower() and char.isalnum():
        return config.MODIFIER_REPEATED

    if char == '\n':
        return config.MODIFIER_NEWLINE
    if char == ' ':
        return config.MODIFIER_SPACE
    if char in config.SPECIAL_CHARS:
        return config.MODIFIER_SPECIAL
    if char in config.PUNCTUATION_CHARS:
        return config.MODIFIER_PUNCTUATION
    if char.isdigit():
        return config.MODIFIER_DIGIT

    modifier = 1.0
    if char.isupper():
        modifier *= config.MODIFIER_CAPITAL
    if char.lower() in config.COMMON_CHARS[:10]:
        modifier *= config.MODIFIER_COMMON

    return modifier


def list_windows(quiet: bool = False) -> list:
    """List all available windows.

    Returns:
        List of window titles
    """
    try:
        windows = pyautogui.getAllWindows()
        titles = [w.title for w in windows if w.title.strip()]

        if not quiet:
            print("Available windows:")
            for i, title in enumerate(titles, 1):
                print(f"  {i}. {title}")

        return titles
    except Exception as e:
        if not quiet:
            print(f"Error listing windows: {e}", file=sys.stderr)
        return []


def activate_window(window_title: str, quiet: bool = False) -> bool:
    """Activate (focus) a window by its title.

    Args:
        window_title: Full or partial window title to match
        quiet: Suppress output

    Returns:
        True if window was activated, False otherwise
    """
    try:
        # Try exact match first
        windows = pyautogui.getWindowsWithTitle(window_title)

        if not windows:
            # Try partial match (case-insensitive)
            all_windows = pyautogui.getAllWindows()
            windows = [w for w in all_windows
                      if window_title.lower() in w.title.lower()]

        if windows:
            target = windows[0]
            if not quiet:
                print(f"Activating window: {target.title}")

            # Restore if minimized
            if target.isMinimized:
                target.restore()

            target.activate()
            time.sleep(0.3)  # Wait for window to activate
            return True
        else:
            if not quiet:
                print(f"Window not found: {window_title}", file=sys.stderr)
                print("Use --list-windows to see available windows")
            return False

    except Exception as e:
        if not quiet:
            print(f"Error activating window: {e}", file=sys.stderr)
        return False


def human_type(text: str, min_delay: float, max_delay: float, quiet: bool = False) -> None:
    """Type text with human-like delays.

    Args:
        text: Text to type
        min_delay: Minimum delay between keystrokes (seconds)
        max_delay: Maximum delay between keystrokes (seconds)
        quiet: Suppress progress output
    """
    # Press ESC before starting to ensure clean state
    keyboard.press(Key.esc)
    keyboard.release(Key.esc)
    time.sleep(0.1)  # Wait for ESC to process

    total = len(text)
    prev_char = ''
    # Rhythm: typing speed drifts over time
    rhythm = 1.0
    rhythm_direction = random.choice([-1, 1])

    for i, char in enumerate(text):
        # Type the character
        type_char(char)

        if not quiet:
            percent = int((i + 1) / total * 100)
            print(f"\rProgress: {i + 1}/{total} ({percent}%)", end="", flush=True)

        # Character-specific delay with rhythm
        base_delay = get_base_delay(min_delay, max_delay)
        modifier = get_char_modifier(char, prev_char)
        time.sleep(base_delay * modifier * rhythm)

        # Update rhythm for natural speed variation
        if random.random() < config.RHYTHM_CHANGE_PROBABILITY:
            rhythm_direction *= -1
        rhythm += rhythm_direction * config.RHYTHM_DRIFT_RATE * random.random()
        if rhythm <= config.RHYTHM_MIN:
            rhythm = config.RHYTHM_MIN
            rhythm_direction = 1
        elif rhythm >= config.RHYTHM_MAX:
            rhythm = config.RHYTHM_MAX
            rhythm_direction = -1

        # Burst typing - extra pause at word boundaries
        if char == ' ':
            pause = random.uniform(config.BURST_WORD_PAUSE_MIN, config.BURST_WORD_PAUSE_MAX)
            time.sleep(pause)

        prev_char = char

    if not quiet:
        print("\nDone!")


def watch_file(filepath: str, min_delay: float, max_delay: float,
               countdown: int, delete_after: bool, window: str | None,
               quiet: bool) -> None:
    """Watch a file and type its contents when it appears.

    Args:
        filepath: Path to watch
        min_delay: Minimum delay between keystrokes
        max_delay: Maximum delay between keystrokes
        countdown: Seconds to wait before typing
        delete_after: Delete file after typing
        window: Window title to activate before typing
        quiet: Suppress output
    """
    if not quiet:
        print(f"Watching for file: {filepath}")
        if window:
            print(f"Target window: {window}")
        print("Press Ctrl+C to stop")

    try:
        while True:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()

                if text.strip():
                    if not quiet:
                        print(f"\nFile found! Content length: {len(text)} chars")

                    # Activate window if specified
                    if window:
                        if not activate_window(window, quiet):
                            if not quiet:
                                print("Skipping typing due to window activation failure")
                            if delete_after:
                                os.remove(filepath)
                            continue

                    # Countdown
                    for i in range(countdown, 0, -1):
                        if not quiet:
                            print(f"Starting in {i}...", flush=True)
                        time.sleep(1)

                    if not quiet:
                        print("Typing...")

                    human_type(text, min_delay, max_delay, quiet)

                    if delete_after:
                        os.remove(filepath)
                        if not quiet:
                            print(f"Deleted: {filepath}")

            time.sleep(0.5)  # Check every 500ms
    except KeyboardInterrupt:
        if not quiet:
            print("\nStopped watching.")


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="human-typer",
        description="Type text with human-like delays",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Type from file after 3 second countdown
  python human_typer.py -f input.txt

  # Type from stdin
  echo "Hello World" | python human_typer.py --stdin

  # Watch mode: type contents when file appears
  python human_typer.py --watch

  # Watch mode with auto window focus
  python human_typer.py --watch --window "Visual Studio Code"

  # List available windows
  python human_typer.py --list-windows

  # Type to specific window
  python human_typer.py -f input.txt --window "Notepad"

  # For Claude/automation: write to watch file
  echo "print('hello')" > ~/.human_typer_input.txt
        """
    )

    # Input source
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "-f", "--file",
        help="File to read and type"
    )
    input_group.add_argument(
        "--stdin",
        action="store_true",
        help="Read from stdin"
    )
    input_group.add_argument(
        "--watch",
        nargs="?",
        const=DEFAULT_WATCH_FILE,
        metavar="FILE",
        help=f"Watch file and type when it appears (default: {DEFAULT_WATCH_FILE})"
    )
    input_group.add_argument(
        "-t", "--text",
        help="Text to type directly"
    )
    input_group.add_argument(
        "--list-windows",
        action="store_true",
        help="List all available windows and exit"
    )

    # Window options
    parser.add_argument(
        "-w", "--window",
        metavar="TITLE",
        help="Activate window with this title before typing (partial match supported)"
    )

    # Timing options
    parser.add_argument(
        "--min-delay",
        type=int,
        default=config.DEFAULT_MIN_DELAY_MS,
        metavar="MS",
        help=f"Minimum delay in ms (default: {config.DEFAULT_MIN_DELAY_MS})"
    )
    parser.add_argument(
        "--max-delay",
        type=int,
        default=config.DEFAULT_MAX_DELAY_MS,
        metavar="MS",
        help=f"Maximum delay in ms (default: {config.DEFAULT_MAX_DELAY_MS})"
    )
    parser.add_argument(
        "-c", "--countdown",
        type=int,
        default=config.DEFAULT_COUNTDOWN_SEC,
        metavar="SEC",
        help=f"Countdown before typing (default: {config.DEFAULT_COUNTDOWN_SEC})"
    )

    # Other options
    parser.add_argument(
        "-d", "--delete",
        action="store_true",
        help="Delete file after typing (for --watch mode)"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress progress output"
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch GUI mode"
    )

    args = parser.parse_args()

    # List windows mode
    if args.list_windows:
        list_windows(args.quiet)
        return 0

    # Convert delays to seconds
    min_delay = args.min_delay / 1000.0
    max_delay = args.max_delay / 1000.0

    # Ensure min <= max
    if min_delay > max_delay:
        min_delay, max_delay = max_delay, min_delay

    # GUI mode
    if args.gui:
        from .__main__ import main as gui_main
        gui_main()
        return 0

    # Watch mode
    if args.watch:
        watch_file(
            args.watch, min_delay, max_delay,
            args.countdown, args.delete, args.window, args.quiet
        )
        return 0

    # Get text to type
    text = None

    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            return 1
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
    elif args.stdin:
        text = sys.stdin.read()
    elif args.text:
        text = args.text
    else:
        # No input specified - show help
        parser.print_help()
        return 0

    if not text or not text.strip():
        print("Error: No text to type", file=sys.stderr)
        return 1

    # Activate window if specified
    if args.window:
        if not activate_window(args.window, args.quiet):
            return 1

    # Countdown
    if not args.quiet:
        print(f"Text length: {len(text)} chars")

    for i in range(args.countdown, 0, -1):
        if not args.quiet:
            print(f"Starting in {i}...", flush=True)
        time.sleep(1)

    if not args.quiet:
        print("Typing...")

    human_type(text, min_delay, max_delay, args.quiet)

    return 0


if __name__ == "__main__":
    sys.exit(main())
