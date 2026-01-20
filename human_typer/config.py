"""Configuration constants for Human-like Typing Tool."""

from dataclasses import dataclass, field


@dataclass
class Config:
    """Application configuration with default values."""

    # Window settings
    WINDOW_TITLE: str = "Human-like Typing Tool"
    WINDOW_MIN_WIDTH: int = 500
    WINDOW_MIN_HEIGHT: int = 400

    # Typing speed defaults (milliseconds)
    # Base delay for normal characters (~100-150 WPM feel)
    DEFAULT_MIN_DELAY_MS: int = 15
    DEFAULT_MAX_DELAY_MS: int = 70

    # Delay ranges (UI slider bounds)
    MIN_DELAY_RANGE: tuple = (1, 500)
    MAX_DELAY_RANGE: tuple = (1, 1000)

    # pyautogui settings
    FAILSAFE_ENABLED: bool = True
    PAUSE_BETWEEN_ACTIONS: float = 0

    # Human-like typing modifiers
    # Multipliers applied to base delay for different character types
    MODIFIER_PUNCTUATION: float = 1.8      # . , ! ? ; : etc.
    MODIFIER_SPECIAL: float = 2.0          # @ # $ % ^ & * etc.
    MODIFIER_CAPITAL: float = 1.4          # Shift key overhead
    MODIFIER_SPACE: float = 1.1            # Word boundary - slight pause
    MODIFIER_NEWLINE: float = 4.0          # Line boundary - thinking pause
    MODIFIER_DIGIT: float = 1.3            # Number row - less familiar
    MODIFIER_REPEATED: float = 0.6         # Same char - finger already there
    MODIFIER_COMMON: float = 0.85          # Common letters - muscle memory

    # Common letters (most frequent in English, typed faster)
    COMMON_CHARS: str = "etaoinshrlducmwfgypbvkjxqz"

    # Punctuation characters
    PUNCTUATION_CHARS: str = ".,!?;:'\"-"

    # Special characters (require shift or are less common)
    SPECIAL_CHARS: str = "@#$%^&*()_+=[]{}\\|<>/`~"

    # Burst typing settings
    BURST_WORD_PAUSE_MIN: float = 0.05     # Min pause after word (seconds)
    BURST_WORD_PAUSE_MAX: float = 0.15     # Max pause after word (seconds)

    # Typing rhythm settings (speed drift over time)
    RHYTHM_DRIFT_RATE: float = 0.08        # How much rhythm changes per character
    RHYTHM_MIN: float = 0.6                # Fastest rhythm (60% of base delay)
    RHYTHM_MAX: float = 1.8                # Slowest rhythm (180% of base delay)
    RHYTHM_CHANGE_PROBABILITY: float = 0.1 # Chance to change drift direction

    # Typo simulation settings
    TYPO_PROBABILITY: float = 0.02         # 2% chance of typo per character
    TYPO_CORRECTION_DELAY: float = 0.15    # Pause before correcting (seconds)
    TYPO_STREAK_PROBABILITY: float = 0.35  # 35% chance of another typo after a typo
    TYPO_STREAK_DECAY: float = 0.6         # Each subsequent typo chance multiplied by this

    # Adjacent keys on QWERTY keyboard for typo simulation
    ADJACENT_KEYS: dict = field(default_factory=lambda: {
        'a': 'sqwz', 'b': 'vghn', 'c': 'xdfv', 'd': 'serfcx', 'e': 'wrsdf',
        'f': 'drtgvc', 'g': 'ftyhbv', 'h': 'gyujnb', 'i': 'ujklo', 'j': 'huiknm',
        'k': 'jiolm', 'l': 'kop', 'm': 'njk', 'n': 'bhjm', 'o': 'iklp',
        'p': 'ol', 'q': 'wa', 'r': 'edft', 's': 'awedxz', 't': 'rfgy',
        'u': 'yhji', 'v': 'cfgb', 'w': 'qase', 'x': 'zsdc', 'y': 'tghu',
        'z': 'asx', '1': '2q', '2': '13qw', '3': '24we', '4': '35er',
        '5': '46rt', '6': '57ty', '7': '68yu', '8': '79ui', '9': '80io', '0': '9op',
    })


# Singleton instance for easy import
config = Config()
