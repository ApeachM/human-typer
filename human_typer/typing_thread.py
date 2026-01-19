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
            pyautogui.write(char, interval=0)
        else:
            # Non-ASCII (Korean, emoji, etc.) - use clipboard
            pyperclip.copy(char)
            pyautogui.hotkey('ctrl', 'v')

    def _get_random_delay(self) -> float:
        """Get a random delay for human-like typing effect."""
        return random.uniform(self.min_delay, self.max_delay)

    def run(self) -> None:
        """Execute the typing process."""
        total = len(self.text)

        for i in range(self.start_pos, total):
            # Update position FIRST (before stop check)
            self._current_pos = i

            if self._stop_flag:
                self.stopped_at.emit(i)
                return

            char = self.text[i]
            self._type_char(char)
            self.char_typed.emit(char)
            self.progress.emit(i + 1, total)

            time.sleep(self._get_random_delay())

        self.finished_typing.emit()
