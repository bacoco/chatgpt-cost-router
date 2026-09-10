#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATE_DIR="${HOME}/.local/state/chatgpt-cost-router/mesh"
PORT="${COST_ROUTER_MESH_PORT:-8790}"
HTTPS_PORT="${COST_ROUTER_MESH_HTTPS_PORT:-8444}"
: "${COST_ROUTER_MESH_ALLOWED_USERS:?Set COST_ROUTER_MESH_ALLOWED_USERS to exact Tailscale login(s)}"
for cmd in python3 tailscale; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "missing required command: $cmd" >&2; exit 2; }
done
tailscale status >/dev/null
mkdir -p "$STATE_DIR"
chmod 700 "$STATE_DIR"
PID_FILE="$STATE_DIR/control.pid"
LOG_FILE="$STATE_DIR/control.log"
if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "mesh control plane already running: pid $(cat "$PID_FILE")"
else
  cd "$ROOT"
  nohup python3 scripts/mesh_control_server.py --host 127.0.0.1 --port "$PORT" \
    >"$LOG_FILE" 2>&1 &
  pid=$!
  echo "$pid" >"$PID_FILE"
  sleep 1
  if ! kill -0 "$pid" 2>/dev/null; then
    echo "mesh control plane failed to start" >&2
    cat "$LOG_FILE" >&2 || true
    exit 3
  fi
  echo "mesh control plane started: pid $pid"
fi
tailscale serve --bg --https="$HTTPS_PORT" "$PORT"
echo "--- Tailscale Serve status ---"
tailscale serve status
echo "--- Local state ---"
echo "backend=http://127.0.0.1:${PORT}"
echo "tailscale_https_port=${HTTPS_PORT}"
echo "registry=${STATE_DIR}/nodes.json"
echo "log=${LOG_FILE}"
echo "Do not use Tailscale Funnel for this service."
