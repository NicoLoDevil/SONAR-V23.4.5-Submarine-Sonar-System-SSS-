"""Main runner for the sonar simulator.

Run in a Codespace or local machine. This is a simulation-only tool and does
not interface with any submarine hardware.
"""
from __future__ import annotations
import numpy as np
import time
from .input import SonarInput
from .ocean import ambient_noise, add_multipath, spherical_spreading_loss
from .beamforming import spherical_array_positions, delay_and_sum
from .processing import matched_filter, compute_stft, simple_cfar, bandpass
from .ui import SonarUI, play_sound
from scipy.io import wavfile
from .tracker import TargetTracker
import logging

logger = logging.getLogger(__name__)


def run_simulation(duration: float = 30.0, ping_interval: float = 3.0, headless: bool = False, outdir: str | None = None):
    si = SonarInput(sample_rate=44100, channels=102)
    if headless and outdir is not None:
        import os
        os.makedirs(outdir, exist_ok=True)
    ui = SonarUI(sample_rate=si.sample_rate, headless=headless, outdir=outdir)
    positions = spherical_array_positions(102, radius=0.5)
    tracker = TargetTracker()

    # Example targets: channel->range mapping for simple simulation
    # Simulate a single target at ~1000m in directions mapped to element indices
    target_ranges = {i: 1000.0 + 100.0 * np.sin(i/10.0) for i in range(0, 102, 8)}

    start = time.time()
    last_ping = start - ping_interval
    times = []
    b_list = []
    m_list = []
    while time.time() - start < duration:
        now = time.time()
        if now - last_ping >= ping_interval:
            last_ping = now
            # generate chirp and play
            chirp_sig = si.generate_chirp(f0=2000, f1=8000, duration=0.2)
            # save a WAV of the ping for download/playback (on first ping)
            if outdir is not None:
                try:
                    wav_path = f"{outdir}/ping.wav"
                    # scale to int16
                    wav = (chirp_sig * 32767).astype('int16')
                    wavfile.write(wav_path, si.sample_rate, wav)
                except Exception:
                    logger.exception('Failed to write ping WAV')
            # create multi-channel echoes
            array_ping = si.make_array_ping(chirp_sig, target_ranges, speed_of_sound=1500.0)
            # add ambient noise
            for ch in range(array_ping.shape[0]):
                array_ping[ch] += ambient_noise(array_ping.shape[1], level=1e-3)

            # simple beamforming scan across bearings
            bearings = np.arange(0, 360, 5)
            mags = []
            for b in bearings:
                bf = delay_and_sum(array_ping, positions, b, 0.0, fs=si.sample_rate, freq=3000.0)
                env = np.abs(matched_filter(bf, chirp_sig))
                mags.append(env.max())

            mags = np.array(mags)
            # pick peaks via simple threshold
            peaks = mags > (mags.mean() + 3*mags.std())
            detected_bearings = bearings[peaks]
            detected_mags = mags[peaks]

            t_rel = now - start
            times.extend([t_rel]*len(detected_bearings))
            b_list.extend(detected_bearings.tolist())
            m_list.extend(detected_mags.tolist())

            # update UI
            ui.update_spectrogram(chirp_sig)
            ui.update_bearing(detected_bearings, detected_mags)
            ui.update_bti(np.array(times), np.array(b_list), np.array(m_list))
            ui.show()

            # play ping synchronous to UI (may fail in headless or no-audio env)
            if not headless:
                try:
                    play_sound(chirp_sig, fs=si.sample_rate)
                except Exception as e:
                    logger.warning('Audio playback failed: %s', e)

        time.sleep(0.1)


if __name__ == '__main__':
    import argparse
    logging.basicConfig(level=logging.INFO)
    p = argparse.ArgumentParser()
    p.add_argument('--duration', type=float, default=60.0)
    p.add_argument('--ping-interval', type=float, default=5.0)
    p.add_argument('--headless', action='store_true')
    p.add_argument('--outdir', type=str, default='sim_outputs')
    args = p.parse_args()
    if args.headless:
        import os
        os.makedirs(args.outdir, exist_ok=True)
    run_simulation(duration=args.duration, ping_interval=args.ping_interval, headless=args.headless, outdir=args.outdir)
