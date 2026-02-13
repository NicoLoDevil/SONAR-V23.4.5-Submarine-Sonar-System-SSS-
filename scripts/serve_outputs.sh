#!/usr/bin/env bash
set -euo pipefail

OUTDIR=${1:-sim_outputs/headless_run}
VENV=${2:-.venv}

if [ ! -d "$OUTDIR" ]; then
  echo "Output directory $OUTDIR does not exist"
  exit 1
fi

if [ ! -x "$VENV/bin/python" ]; then
  echo "Python not found in venv $VENV. Pass venv path as second arg or create .venv"
  exit 1
fi

echo "Generating dashboard and serving $OUTDIR on http://localhost:8000"
"$VENV/bin/python" tools/dashboard.py --outdir "$OUTDIR" --port 8000
