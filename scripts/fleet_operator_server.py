#!/usr/bin/env python3
"""Repository entry point for the Fleet Operator MCP server."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fleet_operator.mcp_server import main

if __name__ == "__main__":
    main()
