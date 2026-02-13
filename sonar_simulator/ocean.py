"""Ocean environment simulator: propagation loss, multipath, and ambient noise.
"""
from __future__ import annotations
import numpy as np
from typing import List, Tuple


def spherical_spreading_loss(range_m: float, freq_khz: float, alpha_db_per_m: float = 0.001) -> float:
    # spherical spreading (20*log10(r)) + absorption (alpha * r)
    if range_m <= 0:
        return 1.0
    spreading = 1.0 / (range_m if range_m>0 else 1.0)
    absorption = 10 ** ( - alpha_db_per_m * freq_khz * range_m / 20.0)
    return spreading * absorption


def add_multipath(signal: np.ndarray, delays: List[float], amps: List[float], fs: int) -> np.ndarray:
    N = len(signal) + int(max(delays)*fs) + 1
    out = np.zeros(N)
    for d, a in zip(delays, amps):
        shift = int(d * fs)
        out[shift:shift+len(signal)] += a * signal
    return out


def ambient_noise(length: int, level: float = 1e-3) -> np.ndarray:
    # Gaussian ambient noise; in more advanced versions use Wenz spectra
    return np.random.normal(scale=level, size=length)
