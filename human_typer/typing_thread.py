"""Typing thread module for human-like text input."""

import random
import time

from PyQt5.QtCore import QThread, pyqtSignal
import pyautogui
import pyperclip

from .config import config


# Configure pyautogui
pyautogui.FAILSAFE = config.FAILSAFE_ENABLED
pyautogui.PAUSE = config.PAUSE_BETWEEN_ACTIONS


class TypingThread(QThread):
    """Background thread that handles typing with human-like delays.

    Signals:
        progress: Emitted after each character (current_pos, total)
        finished_typing: Emitted when typing completes
        stopped_at: Emitted when stopped (position)
        char_typed: Emitted after each character (char)
    """

    progress = pyqtSignal(int, int)
    finished_typing = pyqtSignal()
    stopped_at = pyqtSignal(int)
    char_typed = pyqtSignal(str)

    def __init__(self, text: str, min_delay: float, max_delay: float, start_pos: int = 0):
        """Initialize the typing thread.

        Args:
            text: The text to type
            min_delay: Minimum delay between characters (seconds)
            max_delay: Maximum delay between characters (seconds)
            start_pos: Position to start/resume from
        """
        super().__init__()
        self.text = text
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.start_pos = start_pos
        self._stop_flag = False
        self._current_pos = start_pos
        self._prev_char = ''
        # Rhythm: typing speed drifts over time (like human attention/focus)
        self._rhythm = 1.0  # Current rhythm multiplier
        self._rhythm_direction = random.choice([-1, 1])  # Drifting faster or slower

    def stop(self) -> None:
        """Request the thread to stop."""
        self._stop_flag = True

    @staticmethod
    def _is_ascii(char: str) -> bool:
        """Check if character is ASCII (can be typed directly)."""
        return ord(char) < 128

    def _type_char(self, char: str) -> None:
        """Type a single character using appropriate method.

        Args:
            char: The character to type
        """
        if char == '\n':
            pyautogui.press('enter')
        elif char == '\t':
            pyautogui.press('tab')
        elif self._is_ascii(char):
            # Use small interval for reliable Shift key handling
            pyautogui.write(char, interval=0.01)
        else:
            # Non-ASCII (Korean, emoji, etc.) - use clipboard
            pyperclip.copy(char)
            pyautogui.hotkey('ctrl', 'v')

    def _get_char_modifier(self, char: str) -> float:
        """Get delay modifier based on character type.

        Args:
            char: The character to analyze

        Returns:
            Multiplier for the base delay
        """
        modifier = 1.0

        # Check for repeated character (same finger, faster)
        if char.lower() == self._prev_char.lower() and char.isalnum():
            return config.MODIFIER_REPEATED

        # Newline - thinking pause
        if char == '\n':
            return config.MODIFIER_NEWLINE

        # Space - word boundary
        if char == ' ':
            return config.MODIFIER_SPACE

        # Special characters
        if char in config.SPECIAL_CHARS:
            return config.MODIFIER_SPECIAL

        # Punctuation
        if char in config.PUNCTUATION_CHARS:
            return config.MODIFIER_PUNCTUATION

        # Digits
        if char.isdigit():
            return config.MODIFIER_DIGIT

        # Capital letters (shift key)
        if char.isupper():
            modifier *= config.MODIFIER_CAPITAL

        # Common letters (faster due to muscle memory)
        if char.lower() in config.COMMON_CHARS[:10]:  # Top 10 most common
            modifier *= config.MODIFIER_COMMON

        return modifier

    def _get_base_delay(self) -> float:
        """Get base delay using exponential distribution."""
        delay_range = self.max_delay - self.min_delay
        if delay_range <= 0:
            return self.min_delay

        extra_delay = random.expovariate(3.0 / delay_range)
        return min(self.min_delay + extra_delay, self.max_delay)

    def _update_rhythm(self) -> None:
        """Update typing rhythm - speed drifts over time like human focus."""
        # Randomly change direction sometimes
        if random.random() < config.RHYTHM_CHANGE_PROBABILITY:
            self._rhythm_direction *= -1

        # Drift the rhythm
        self._rhythm += self._rhythm_direction * config.RHYTHM_DRIFT_RATE * random.random()

        # Clamp to bounds and bounce off edges
        if self._rhythm <= config.RHYTHM_MIN:
            self._rhythm = config.RHYTHM_MIN
            self._rhythm_direction = 1  # Start slowing down
        elif self._rhythm >= config.RHYTHM_MAX:
            self._rhythm = config.RHYTHM_MAX
            self._rhythm_direction = -1  # Start speeding up

    def _get_random_delay(self, char: str) -> float:
        """Get delay adjusted for character type and current rhythm.

        Args:
            char: Current character being typed

        Returns:
            Delay in seconds
        """
        base_delay = self._get_base_delay()
        modifier = self._get_char_modifier(char)
        return base_delay * modifier * self._rhythm

    def _add_burst_pause(self, char: str) -> None:
        """Add extra pause at word boundaries for burst typing effect.

        Args:
            char: Character just typed
        """
        if char == ' ':
            # Small pause after completing a word
            pause = random.uniform(
                config.BURST_WORD_PAUSE_MIN,
                config.BURST_WORD_PAUSE_MAX
            )
            time.sleep(pause)

    def run(self) -> None:
        """Execute the typing process."""
        total = len(self.text)

        for i in range(self.start_pos, total):
            self._current_pos = i

            if self._stop_flag:
                self.stopped_at.emit(i)
                return

            char = self.text[i]

            # Type the character
            self._type_char(char)

            self.char_typed.emit(char)
            self.progress.emit(i + 1, total)

            # Character-specific delay
            time.sleep(self._get_random_delay(char))

            # Update rhythm for natural speed variation
            self._update_rhythm()

            # Burst typing - extra pause at word boundaries
            self._add_burst_pause(char)

            # Update previous character for next iteration
            self._prev_char = char

        self.finished_typing.emit()
