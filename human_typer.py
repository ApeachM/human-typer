#!/usr/bin/env python3
"""
Human-like Typing Tool - Entry Point

Usage:
    python human_typer.py          # GUI mode
    python human_typer.py --help   # CLI help
    python human_typer.py -f file  # CLI mode
"""

import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        from human_typer.cli import main
        sys.exit(main())
    else:
        from human_typer.__main__ import main
        main()
