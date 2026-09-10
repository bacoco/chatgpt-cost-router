#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATE_DIR="${HOME}/.local/state/chatgpt-cost-router/remote-worker"
PORT="${COST_ROUTER_REMOTE_PORT:-8787}"
HTTPS_PORT="${COST_ROUTER_TAILSCALE_HTTPS_PORT:-8443}"

: "${COST_ROUTER_ALLOWED_TAILSCALE_USERS:?Set COST_ROUTER_ALLOWED_TAILSCALE_USERS to the exact Tailscale login(s) allowed to use this worker}"
export COST_ROUTER_REMOTE_WORKERS="${COST_ROUTER_REMOTE_WORKERS:-openai-B}"
export COST_ROUTER_REMOTE_WORKSPACE_ROOT="${COST_ROUTER_REMOTE_WORKSPACE_ROOT:-${HOME}/codex-remote-worker-tasks}"

for cmd in python3 codex tailscale; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "missing required command: $cmd" >&2; exit 2; }
done

tailscale status >/dev/null
mkdir -p "$STATE_DIR" "$COST_ROUTER_REMOTE_WORKSPACE_ROOT"
chmod 700 "$STATE_DIR" "$COST_ROUTER_REMOTE_WORKSPACE_ROOT"
PID_FILE="$STATE_DIR/server.pid"
LOG_FILE="$STATE_DIR/server.log"

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "remote worker backend already running: pid $(cat "$PID_FILE")"
else
  cd "$ROOT"
  nohup python3 scripts/remote_worker_server.py --host 127.0.0.1 --port "$PORT" \
    >"$LOG_FILE" 2>&1 &
  pid=$!
  echo "$pid" >"$PID_FILE"
  sleep 1
  if ! kill -0 "$pid" 2>/dev/null; then
    echo "remote worker backend failed to start" >&2
    cat "$LOG_FILE" >&2 || true
    exit 3
  fi
  echo "remote worker backend started: pid $pid"
fi

# Dedicated HTTPS port avoids disturbing an existing Serve mapping on 443.
tailscale serve --bg --https="$HTTPS_PORT" "$PORT"
echo "--- Tailscale Serve status ---"
tailscale serve status

echo "--- Local state ---"
echo "backend=http://127.0.0.1:${PORT}"
echo "tailscale_https_port=${HTTPS_PORT}"
echo "allowed_workers=${COST_ROUTER_REMOTE_WORKERS}"
echo "log=${LOG_FILE}"
echo "Do not use Tailscale Funnel for this service."
