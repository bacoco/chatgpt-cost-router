"""Stable absolute script entry point for the owned process supervisor."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from fleet_operator.jobs.worker import main

if __name__ == "__main__":
    raise SystemExit(main())
