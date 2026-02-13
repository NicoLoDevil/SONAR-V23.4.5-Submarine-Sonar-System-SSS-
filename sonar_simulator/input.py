"""Data acquisition and ping generation.

Simulation-only: supports synthetic chirp generation, WAV file input,
and optional live microphone input (via PyAudio or sounddevice).
"""
from __future__ import annotations
import numpy as np
from scipy.signal import chirp
from dataclasses import dataclass
import wave
import logging

logger = logging.getLogger(__name__)


@dataclass
class SonarInput:
    sample_rate: int = 44100
    channels: int = 102
    dtype: str = 'float32'

    def generate_chirp(self, f0: float = 2000.0, f1: float = 8000.0, duration: float = 0.2) -> np.ndarray:
        """Generate an LFM chirp (linear frequency modulation).

        Returns a single-channel numpy array representing the chirp.
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        sig = chirp(t, f0=f0, f1=f1, t1=duration, method='linear')
        # apply smooth window
        win = np.hanning(len(sig))
        return (sig * win).astype(self.dtype)

    def make_array_ping(self, chirp_signal: np.ndarray, ranges: dict, speed_of_sound: float = 1500.0) -> np.ndarray:
        """Simulate multi-channel array returns for targets described in ranges.

        ranges: mapping of channel_index -> range_in_meters to simulate different delays.
        Returns: array of shape (channels, len(chirp_signal)+max_delay_samples)
        """
        max_range = max(ranges.values()) if ranges else 0.0
        max_delay = int((2 * max_range / speed_of_sound) * self.sample_rate)
        out_len = len(chirp_signal) + max_delay + 10
        out = np.zeros((self.channels, out_len), dtype=self.dtype)
        for ch in range(self.channels):
            r = ranges.get(ch, None)
            if r is None:
                continue
            delay_samples = int((2 * r / speed_of_sound) * self.sample_rate)
            amp = 1.0 / (1.0 + r/1000.0)
            out[ch, delay_samples:delay_samples+len(chirp_signal)] += amp * chirp_signal
        return out

    def read_wav(self, path: str) -> np.ndarray:
        """Read mono WAV and return float32 numpy array."""
        with wave.open(path, 'rb') as wf:
            n_channels = wf.getnchannels()
            frames = wf.readframes(wf.getnframes())
            data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
            if n_channels > 1:
                data = data.reshape(-1, n_channels).T
            else:
                data = data[np.newaxis, :]
            return data
