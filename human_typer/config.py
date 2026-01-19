"""Configuration constants for Human-like Typing Tool."""

from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration with default values."""

    # Window settings
    WINDOW_TITLE: str = "Human-like Typing Tool"
    WINDOW_MIN_WIDTH: int = 500
    WINDOW_MIN_HEIGHT: int = 400

    # Typing speed defaults (milliseconds)
    # Based on fast developer typing speed (~100 WPM)
    DEFAULT_MIN_DELAY_MS: int = 40
    DEFAULT_MAX_DELAY_MS: int = 100

    # Delay ranges
    MIN_DELAY_RANGE: tuple = (1, 500)
    MAX_DELAY_RANGE: tuple = (1, 1000)

    # pyautogui settings
    FAILSAFE_ENABLED: bool = True
    PAUSE_BETWEEN_ACTIONS: float = 0


# Singleton instance for easy import
config = Config()
