#!/usr/bin/env python3
"""Supervised safe relay; historic ledger is migrated without replay."""
import argparse
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from fleet_operator.relay import RelayConfig
from fleet_operator.relay_service import run_forever, run_once


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",required=True)
    parser.add_argument("--once",action="store_true")
    args = parser.parse_args()
    config = RelayConfig.load(args.config)
    if args.once:
        import json
        print(json.dumps(run_once(config),indent=2))
    else:
        run_forever(config)


if __name__ == "__main__":
    main()
