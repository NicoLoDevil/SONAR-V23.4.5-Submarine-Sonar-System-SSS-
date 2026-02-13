#!/usr/bin/env bash
set -euo pipefail

echo "This script installs PortAudio dev headers on Debian/Ubuntu."

if [ "$EUID" -ne 0 ]; then
  echo "This script requires sudo. Re-running with sudo..."
  exec sudo bash "$0" "$@"
fi

apt-get update
apt-get install -y portaudio19-dev build-essential python3-dev

echo "Done. Activate your project's venv and reinstall Python deps:" 
cat <<'CMD'
source .venv/bin/activate
pip install --upgrade --force-reinstall -r requirements.txt
CMD
