"""Main window module for Human-like Typing Tool."""

import time
import platform
import subprocess
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QSpinBox, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut
import pyautogui

from .config import config
from .typing_thread import TypingThread


def get_active_window_linux() -> str | None:
    """Get the active window title on Linux using xprop."""
    try:
        # Get active window ID
        result = subprocess.run(
            ["xprop", "-root", "_NET_ACTIVE_WINDOW"],
            capture_output=True, text=True, timeout=1
        )
        if result.returncode != 0:
            return None

        # Parse window ID
        parts = result.stdout.strip().split()
        if len(parts) < 5:
            return None
        window_id = parts[4]

        if window_id == "0x0":
            return None

        # Get window name
        result = subprocess.run(
            ["xprop", "-id", window_id, "_NET_WM_NAME"],
            capture_output=True, text=True, timeout=1
        )
        if result.returncode == 0 and "=" in result.stdout:
            # Parse: _NET_WM_NAME(UTF8_STRING) = "Window Title"
            name = result.stdout.split("=", 1)[1].strip().strip('"')
            return name

        # Fallback to WM_NAME
        result = subprocess.run(
            ["xprop", "-id", window_id, "WM_NAME"],
            capture_output=True, text=True, timeout=1
        )
        if result.returncode == 0 and "=" in result.stdout:
            name = result.stdout.split("=", 1)[1].strip().strip('"')
            return name

        return None
    except Exception:
        return None


def get_active_window() -> str | None:
    """Get the active window title (cross-platform)."""
    system = platform.system()

    if system == "Linux":
        return get_active_window_linux()
    else:
        # Windows/macOS - use pyautogui
        try:
            win = pyautogui.getActiveWindow()
            if win and win.title:
                return win.title.strip()
        except Exception:
            pass
        return None


def activate_window_linux(window_title: str) -> bool:
    """Activate a window by title on Linux using wmctrl or xdotool."""
    try:
        # Try wmctrl first
        result = subprocess.run(
            ["wmctrl", "-a", window_title],
            capture_output=True, timeout=2
        )
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass
    except Exception:
        pass

    try:
        # Try xdotool
        result = subprocess.run(
            ["xdotool", "search", "--name", window_title, "windowactivate"],
            capture_output=True, timeout=2
        )
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass
    except Exception:
        pass

    # Fallback: use xprop to find window and xdotool/wmctrl
    try:
        # Get all window IDs
        result = subprocess.run(
            ["xprop", "-root", "_NET_CLIENT_LIST"],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode != 0:
            return False

        # Parse window IDs
        line = result.stdout.strip()
        if "#" not in line:
            return False

        window_ids = line.split("#")[1].strip().split(", ")

        for wid in window_ids:
            wid = wid.strip()
            # Get window name
            name_result = subprocess.run(
                ["xprop", "-id", wid, "_NET_WM_NAME"],
                capture_output=True, text=True, timeout=1
            )
            if name_result.returncode == 0 and window_title.lower() in name_result.stdout.lower():
                # Activate this window
                subprocess.run(
                    ["xprop", "-id", wid, "-f", "_NET_ACTIVE_WINDOW", "32c",
                     "-set", "_NET_ACTIVE_WINDOW", "1"],
                    timeout=1
                )
                return True
    except Exception:
        pass

    return False


def activate_window_by_title(window_title: str) -> bool:
    """Activate a window by title (cross-platform)."""
    system = platform.system()

    if system == "Linux":
        return activate_window_linux(window_title)
    else:
        # Windows/macOS - use pyautogui
        try:
            windows = pyautogui.getWindowsWithTitle(window_title)
            if not windows:
                # Try partial match
                all_windows = pyautogui.getAllWindows()
                windows = [w for w in all_windows
                           if window_title.lower() in w.title.lower()]

            if windows:
                target = windows[0]
                if target.isMinimized:
                    target.restore()
                target.activate()
                return True
        except Exception:
            pass
        return False


class HumanTyper(QMainWindow):
    """Main application window for Human-like Typing Tool.

    Provides a GUI interface for:
    - Entering text to be typed
    - Configuring typing speed
    - Starting, stopping, and resuming typing
    - Selecting target window
    """

    def __init__(self):
        super().__init__()
        self._typing_thread: TypingThread | None = None
        self._current_pos: int = 0
        self._last_text: str = ""
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setMinimumSize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT + 50)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add UI components
        layout.addWidget(self._create_text_input_group())
        layout.addWidget(self._create_window_group())
        layout.addWidget(self._create_settings_group())
        layout.addWidget(self._create_status_section())
        layout.addLayout(self._create_button_layout())
        layout.addWidget(self._create_instructions())

    def _create_text_input_group(self) -> QGroupBox:
        """Create the text input area."""
        group = QGroupBox("Text to Type")
        layout = QVBoxLayout(group)

        self._text_edit = QTextEdit()
        self._text_edit.setPlaceholderText("Paste your code or text here...")
        self._text_edit.setAcceptRichText(False)
        self._text_edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._text_edit)

        return group

    def _on_text_changed(self) -> None:
        """Reset position when text is modified."""
        self._current_pos = 0
        self._last_text = ""
        self._progress_label.setText("")

    def _create_window_group(self) -> QGroupBox:
        """Create the target window selection area."""
        group = QGroupBox("Target Window")
        main_layout = QVBoxLayout(group)

        # Current window detection row
        detect_layout = QHBoxLayout()

        detect_layout.addWidget(QLabel("Detected:"))
        self._detected_window_label = QLabel("(none)")
        self._detected_window_label.setStyleSheet(
            "font-weight: bold; color: #0066cc; padding: 2px 8px; "
            "background-color: #f0f0f0; border-radius: 3px;"
        )
        self._detected_window_label.setMinimumWidth(250)
        detect_layout.addWidget(self._detected_window_label)

        # Fix button
        self._fix_btn = QPushButton("Fix")
        self._fix_btn.setToolTip("Lock the current detected window as target")
        self._fix_btn.setCheckable(True)
        self._fix_btn.clicked.connect(self._toggle_fix_window)
        detect_layout.addWidget(self._fix_btn)

        detect_layout.addStretch()
        main_layout.addLayout(detect_layout)

        # Fixed window display row
        fixed_layout = QHBoxLayout()
        fixed_layout.addWidget(QLabel("Target:"))
        self._fixed_window_label = QLabel("(auto - will use detected window)")
        self._fixed_window_label.setStyleSheet("color: gray;")
        fixed_layout.addWidget(self._fixed_window_label)

        # Clear button
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setToolTip("Clear the fixed window selection")
        self._clear_btn.clicked.connect(self._clear_fixed_window)
        self._clear_btn.setEnabled(False)
        fixed_layout.addWidget(self._clear_btn)

        fixed_layout.addStretch()
        main_layout.addLayout(fixed_layout)

        # Start window detection timer
        self._fixed_window_title = ""
        self._detection_timer = QTimer()
        self._detection_timer.timeout.connect(self._detect_current_window)
        self._detection_timer.start(300)  # Check every 300ms

        return group

    def _detect_current_window(self) -> None:
        """Detect the currently focused window."""
        if self._fix_btn.isChecked():
            return  # Don't update while fix mode is active

        try:
            title = get_active_window()
            if title and title != config.WINDOW_TITLE:
                # Truncate long titles for display
                display_title = title if len(title) <= 50 else title[:47] + "..."
                self._detected_window_label.setText(display_title)
                self._detected_window_label.setToolTip(title)
        except Exception:
            pass

    def _toggle_fix_window(self) -> None:
        """Toggle fix window mode."""
        if self._fix_btn.isChecked():
            # Fix the current detected window (use tooltip for full title)
            detected = self._detected_window_label.toolTip() or self._detected_window_label.text()
            if detected and detected != "(none)":
                self._fixed_window_title = detected
                display_title = detected if len(detected) <= 50 else detected[:47] + "..."
                self._fixed_window_label.setText(display_title)
                self._fixed_window_label.setToolTip(detected)
                self._fixed_window_label.setStyleSheet(
                    "font-weight: bold; color: #006600;"
                )
                self._fix_btn.setText("Fixed")
                self._fix_btn.setStyleSheet("background-color: #90EE90;")
                self._clear_btn.setEnabled(True)
                self._status_label.setText(f"Target fixed: {display_title}")
            else:
                self._fix_btn.setChecked(False)
                self._status_label.setText("No window detected to fix")
        else:
            # Unfix
            self._clear_fixed_window()

    def _clear_fixed_window(self) -> None:
        """Clear the fixed window selection."""
        self._fixed_window_title = ""
        self._fixed_window_label.setText("(auto - will use detected window)")
        self._fixed_window_label.setStyleSheet("color: gray;")
        self._fix_btn.setChecked(False)
        self._fix_btn.setText("Fix")
        self._fix_btn.setStyleSheet("")
        self._clear_btn.setEnabled(False)
        self._status_label.setText("Target cleared - will use detected window")

    def _create_settings_group(self) -> QGroupBox:
        """Create the typing speed settings area."""
        group = QGroupBox("Settings")
        layout = QHBoxLayout(group)

        # Min delay
        layout.addWidget(QLabel("Min Delay (ms):"))
        self._min_delay_spin = QSpinBox()
        self._min_delay_spin.setRange(*config.MIN_DELAY_RANGE)
        self._min_delay_spin.setValue(config.DEFAULT_MIN_DELAY_MS)
        layout.addWidget(self._min_delay_spin)

        # Max delay
        layout.addWidget(QLabel("Max Delay (ms):"))
        self._max_delay_spin = QSpinBox()
        self._max_delay_spin.setRange(*config.MAX_DELAY_RANGE)
        self._max_delay_spin.setValue(config.DEFAULT_MAX_DELAY_MS)
        layout.addWidget(self._max_delay_spin)

        layout.addStretch()
        return group

    def _create_status_section(self) -> QWidget:
        """Create the status display section."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self._status_label = QLabel("Status: Ready")
        self._status_label.setAlignment(Qt.AlignCenter)
        self._status_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 10px;"
        )
        layout.addWidget(self._status_label)

        self._progress_label = QLabel("")
        self._progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._progress_label)

        return container

    def _create_button_layout(self) -> QHBoxLayout:
        """Create the control buttons."""
        layout = QHBoxLayout()

        self._start_button = QPushButton("Start (Ctrl+Enter)")
        self._start_button.setMinimumHeight(40)
        self._start_button.clicked.connect(self._on_start_clicked)
        layout.addWidget(self._start_button)

        self._stop_button = QPushButton("Stop")
        self._stop_button.setMinimumHeight(40)
        self._stop_button.setEnabled(False)
        # Use pressed instead of clicked so stop happens immediately on mouse down
        self._stop_button.pressed.connect(self._stop_typing)
        layout.addWidget(self._stop_button)

        # Keyboard shortcut for Start
        start_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        start_shortcut.activated.connect(self._on_start_clicked)

        return layout

    def _create_instructions(self) -> QLabel:
        """Create the instruction label."""
        instructions = QLabel(
            "Instructions:\n"
            "1. Paste text above\n"
            "2. Click target window → 'Detected' updates → (optional) Click 'Fix' to lock\n"
            "3. Click 'Start' → Target window auto-focuses → Typing begins immediately"
        )
        instructions.setStyleSheet("color: gray; font-size: 11px;")
        return instructions

    def _activate_target_window(self) -> bool:
        """Activate the selected target window."""
        # Use fixed window if set, otherwise use the last detected window
        if self._fixed_window_title:
            window_title = self._fixed_window_title
        else:
            window_title = self._detected_window_label.toolTip() or self._detected_window_label.text()
            if window_title == "(none)" or not window_title:
                return True  # No window to activate

        if activate_window_by_title(window_title):
            time.sleep(0.3)
            return True
        else:
            self._status_label.setText(f"Window not found: {window_title}")
            return False

    def _on_start_clicked(self) -> None:
        """Handle Start button click."""
        text = self._text_edit.toPlainText()
        if not text:
            self._status_label.setText("Status: No text to type!")
            return

        # Get target window (fixed or detected)
        window_title = self._get_target_window()
        if not window_title:
            self._status_label.setText("Status: No target window! Click a window first.")
            return

        self._start_button.setEnabled(False)
        self._stop_button.setEnabled(True)
        self._text_edit.setEnabled(False)

        # Activate target window and start typing
        if not self._activate_target_window():
            self._reset_ui()
            return

        self._start_typing()

    def _get_target_window(self) -> str | None:
        """Get the target window title (fixed or detected)."""
        if self._fixed_window_title:
            return self._fixed_window_title

        detected = self._detected_window_label.toolTip() or self._detected_window_label.text()
        if detected and detected != "(none)":
            return detected

        return None

    def _cleanup_typing_thread(self) -> None:
        """Clean up the existing typing thread."""
        if self._typing_thread is not None:
            # Ensure thread is fully stopped
            if self._typing_thread.isRunning():
                self._typing_thread.stop()
                while self._typing_thread.isRunning():
                    self._typing_thread.wait(50)
            try:
                self._typing_thread.progress.disconnect()
                self._typing_thread.finished_typing.disconnect()
                self._typing_thread.stopped_at.disconnect()
            except Exception:
                pass
            self._typing_thread = None

    def _start_typing(self) -> None:
        """Start the typing thread."""
        # Clean up old thread first
        self._cleanup_typing_thread()

        text = self._text_edit.toPlainText()
        min_delay = self._min_delay_spin.value() / 1000.0
        max_delay = self._max_delay_spin.value() / 1000.0

        # Ensure min <= max
        if min_delay > max_delay:
            min_delay, max_delay = max_delay, min_delay

        # Reset position if text changed
        if text != self._last_text:
            self._current_pos = 0
            self._last_text = text

        if self._current_pos > 0:
            self._status_label.setText(f"Status: Resuming from {self._current_pos}...")
        else:
            self._status_label.setText("Status: Typing...")

        self._typing_thread = TypingThread(text, min_delay, max_delay, self._current_pos)
        self._typing_thread.progress.connect(self._update_progress)
        self._typing_thread.finished_typing.connect(self._typing_finished)
        self._typing_thread.stopped_at.connect(self._on_stopped_at)
        self._typing_thread.start()

    def _update_progress(self, current: int, total: int) -> None:
        """Update progress display."""
        percent = int(current / total * 100)
        self._progress_label.setText(f"Progress: {current}/{total} ({percent}%)")

    def _on_stopped_at(self, pos: int) -> None:
        """Handle stopped position from typing thread."""
        self._current_pos = pos

    def _stop_typing(self) -> None:
        """Stop the typing thread."""
        if self._typing_thread:
            self._typing_thread.stop()
            # Wait until thread fully stops (no timeout)
            while self._typing_thread.isRunning():
                self._typing_thread.wait(50)
            # Get position directly from thread before cleanup
            self._current_pos = self._typing_thread._current_pos
            self._cleanup_typing_thread()

        self._reset_ui()
        total = len(self._text_edit.toPlainText())

        if 0 < self._current_pos < total:
            percent = int(self._current_pos / total * 100)
            self._status_label.setText(f"Status: Paused at {self._current_pos}/{total}")
            self._progress_label.setText(
                f"Progress: {self._current_pos}/{total} ({percent}%) - Press Start to resume"
            )
        else:
            self._status_label.setText("Status: Stopped")

    def _typing_finished(self) -> None:
        """Handle typing completion."""
        self._current_pos = 0
        self._reset_ui()
        self._status_label.setText("Status: Completed!")

    def _reset_ui(self) -> None:
        """Reset UI elements to initial state."""
        self._start_button.setEnabled(True)
        self._stop_button.setEnabled(False)
        self._text_edit.setEnabled(True)

    def closeEvent(self, event) -> None:
        """Handle window close."""
        self._stop_typing()
        event.accept()
