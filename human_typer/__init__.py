"""
Human-like Typing Tool
A PyQt5 GUI application that types text with human-like random delays.
"""

__version__ = "1.0.0"
__author__ = "Human Typer Team"

from .main_window import HumanTyper
from .typing_thread import TypingThread
from .config import Config
from .cli import main as cli_main

__all__ = ["HumanTyper", "TypingThread", "Config", "cli_main"]
