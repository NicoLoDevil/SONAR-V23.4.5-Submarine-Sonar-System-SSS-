#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=${1:-.venv}
PY_BIN="$VENV_DIR/bin/python"

if [ ! -x "$PY_BIN" ]; then
  echo "Python binary not found at $PY_BIN"
  echo "Activate your venv or pass its path as first arg, e.g.: .venv"
  exit 1
fi

# Run simulator interactively (non-headless)
"$PY_BIN" -m sonar_simulator.main --duration 60
