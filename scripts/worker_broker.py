#!/usr/bin/env python3
"""CLI for the two-worker Codex broker prototype."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cost_router.workers import WorkerError, load_registry, probe, run_task, select_worker


def main(argv=None):
    parser = argparse.ArgumentParser(description="Probe and dispatch to isolated Codex CLI workers")
    parser.add_argument("--registry", default="examples/workers.json")
    parser.add_argument("--codex-bin", default="codex")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    sub.add_parser("probe")
    dispatch = sub.add_parser("run")
    dispatch.add_argument("--worker", default="auto")
    dispatch.add_argument("--workspace", required=True)
    dispatch.add_argument("--prompt", required=True)
    args = parser.parse_args(argv)

    try:
        workers = load_registry(args.registry)
        if args.command == "list":
            payload = [
                {
                    "id": w.id,
                    "provider": w.provider,
                    "adapter": w.adapter,
                    "cost_class": w.cost_class,
                    "priority": w.priority,
                    "enabled": w.enabled,
                }
                for w in workers
            ]
            print(json.dumps(payload, indent=2))
            return 0
        if args.command == "probe":
            payload = [probe(w, codex_bin=args.codex_bin) for w in workers]
            print(json.dumps(payload, indent=2))
            return 0 if any(item["ready"] for item in payload) else 3
        worker, probes = select_worker(workers, args.worker, codex_bin=args.codex_bin)
        result = run_task(worker, args.prompt, args.workspace, codex_bin=args.codex_bin)
        result["selection_probes"] = probes
        print(json.dumps(result, indent=2))
        return 0 if result["exit_code"] == 0 else result["exit_code"] or 1
    except (OSError, ValueError, WorkerError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
