"""Entry point for running human_typer as a module."""

import sys


def main() -> None:
    """GUI application entry point."""
    from PyQt5.QtWidgets import QApplication
    from .main_window import HumanTyper

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = HumanTyper()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    # Check if any CLI arguments provided
    if len(sys.argv) > 1:
        from .cli import main as cli_main
        sys.exit(cli_main())
    else:
        main()
