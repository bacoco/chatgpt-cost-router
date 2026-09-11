#!/usr/bin/env python3
"""Stable operator-controlled dispatcher for an activated immutable runtime."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fleet_operator.enrollment.cli import active_main
if __name__ == "__main__":
    raise SystemExit(active_main())
