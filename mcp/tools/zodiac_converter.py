#!/usr/bin/env python3
"""Compatibility entry point; implementation lives in the application package."""
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fortune_teller.calculators.zodiac_converter import *  # noqa: F403
from fortune_teller.calculators.zodiac_converter import main

if __name__ == "__main__":
    main()
