#!/usr/bin/env bash
set -euo pipefail
STATE_DIR="${HOME}/.local/state/chatgpt-cost-router/mesh-node"
PID_FILE="$STATE_DIR/agent.pid"
if [[ -f "$PID_FILE" ]]; then
  pid="$(cat "$PID_FILE")"
  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid"
    echo "stopped mesh node agent pid $pid"
  fi
  rm -f "$PID_FILE"
fi
