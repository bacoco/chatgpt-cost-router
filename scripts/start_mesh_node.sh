#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATE_DIR="${HOME}/.local/state/chatgpt-cost-router/mesh-node"
: "${COST_ROUTER_MESH_CONTROL_URL:?Set COST_ROUTER_MESH_CONTROL_URL to the control-plane Tailscale Serve URL}"
export COST_ROUTER_REMOTE_WORKERS="${COST_ROUTER_REMOTE_WORKERS:-openai-B}"
mkdir -p "$STATE_DIR"
chmod 700 "$STATE_DIR"
PID_FILE="$STATE_DIR/agent.pid"
LOG_FILE="$STATE_DIR/agent.log"
if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "mesh node agent already running: pid $(cat "$PID_FILE")"
  exit 0
fi
cd "$ROOT"
nohup python3 scripts/mesh_node_agent.py \
  --control-url "$COST_ROUTER_MESH_CONTROL_URL" \
  --workers "$COST_ROUTER_REMOTE_WORKERS" \
  --interval "${COST_ROUTER_MESH_HEARTBEAT_SECONDS:-30}" \
  >"$LOG_FILE" 2>&1 &
pid=$!
echo "$pid" >"$PID_FILE"
sleep 1
if ! kill -0 "$pid" 2>/dev/null; then
  echo "mesh node agent failed to start" >&2
  cat "$LOG_FILE" >&2 || true
  exit 3
fi
echo "mesh node agent started: pid $pid"
echo "control=$COST_ROUTER_MESH_CONTROL_URL"
echo "workers=$COST_ROUTER_REMOTE_WORKERS"
echo "log=$LOG_FILE"
