Audio setup and interactive run

This repository runs headless in restricted environments (no sudo / no audio).

To enable interactive audio playback on a Debian/Ubuntu host:

1. Run the system setup script (requires sudo):

```bash
bash scripts/install_system_deps.sh
```

2. Activate your virtual environment and reinstall Python deps:

```bash
source .venv/bin/activate
pip install --upgrade --force-reinstall -r requirements.txt
```

3. Run the simulator interactively (non-headless):

```bash
bash scripts/run_interactive.sh .venv
```
If you prefer a browser-based viewer that does not require audio backends,
run the simulator headless to produce frames and WAVs, then serve the output
directory with the dashboard tool:

```bash
# run headless simulation and save outputs
.venv/bin/python -m sonar_simulator.main --duration 10 --ping-interval 2 --headless --outdir sim_outputs/headless_run

# generate index and serve (open http://localhost:8000)
bash scripts/serve_outputs.sh sim_outputs/headless_run .venv
```

The dashboard shows saved frames and provides an audio player for `ping.wav`.

Notes:
- If you prefer, run the apt commands directly instead of the script.
- In the dev container used here we cannot run `sudo`, so the script must be run on a host where you have administrative privileges.
- For CI or headless runs use `--headless` and `--outdir` to save frames and WAV files.
