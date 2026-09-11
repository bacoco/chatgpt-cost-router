#!/usr/bin/env python3
"""Plan enrollment, stage releases and render user services; no implicit deployment."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fleet_operator.enrollment.cli import main
if __name__ == "__main__":
    raise SystemExit(main())
