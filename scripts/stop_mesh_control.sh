#!/usr/bin/env bash
set -euo pipefail
STATE_DIR="${HOME}/.local/state/chatgpt-cost-router/mesh"
PID_FILE="$STATE_DIR/control.pid"
HTTPS_PORT="${COST_ROUTER_MESH_HTTPS_PORT:-8444}"
if command -v tailscale >/dev/null 2>&1; then
  tailscale serve --https="$HTTPS_PORT" off || true
fi
if [[ -f "$PID_FILE" ]]; then
  pid="$(cat "$PID_FILE")"
  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid"
    echo "stopped mesh control plane pid $pid"
  fi
  rm -f "$PID_FILE"
fi
