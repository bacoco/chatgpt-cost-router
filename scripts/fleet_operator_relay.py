#!/usr/bin/env python3
"""Poll the GitHub Fleet Operator command branch and execute bounded jobs."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fleet_operator.relay import RelayConfig, run_forever, run_once


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="~/.config/chatgpt-cost-router/fleet-relay.json")
    p.add_argument("--once", action="store_true")
    args = p.parse_args(argv)
    cfg = RelayConfig.load(args.config)
    if args.once:
        print(json.dumps(run_once(cfg), indent=2))
        return 0
    run_forever(cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
