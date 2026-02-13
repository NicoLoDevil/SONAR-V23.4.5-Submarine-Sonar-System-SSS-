"""Signal processing pipeline: filtering, matched filter, STFT, CFAR detection.
"""
from __future__ import annotations
import numpy as np
from scipy.signal import butter, sosfiltfilt, stft, correlate
from typing import Tuple


def bandpass(signal: np.ndarray, fs: int, low: float, high: float, order: int = 4) -> np.ndarray:
    sos = butter(order, [low / (0.5*fs), high / (0.5*fs)], btype='band', output='sos')
    return sosfiltfilt(sos, signal)


def decimate(signal: np.ndarray, q: int) -> np.ndarray:
    return signal[::q]


def matched_filter(received: np.ndarray, template: np.ndarray) -> np.ndarray:
    """Perform matched filtering via correlation, returns envelope-like array."""
    return correlate(received, template, mode='full')


def simple_cfar(data: np.ndarray, guard: int = 5, noise_win: int = 20, rate: float = 1e-3) -> np.ndarray:
    # Very simplified CFAR: sliding average noise estimate and threshold multiplier
    N = len(data)
    out = np.zeros_like(data, dtype=bool)
    for i in range(N):
        left_start = max(0, i - guard - noise_win)
        left_end = max(0, i - guard)
        right_start = min(N, i + guard + 1)
        right_end = min(N, i + guard + 1 + noise_win)
        noise_samples = np.concatenate((data[left_start:left_end], data[right_start:right_end]))
        if len(noise_samples) < 1:
            continue
        noise_level = np.mean(np.abs(noise_samples))
        threshold = noise_level * (1 + 3*np.sqrt(-np.log(rate)))
        out[i] = np.abs(data[i]) > threshold
    return out


def compute_stft(signal: np.ndarray, fs: int, nperseg: int = 1024, noverlap: int = 512) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    f, t, Zxx = stft(signal, fs=fs, nperseg=nperseg, noverlap=noverlap)
    return f, t, np.abs(Zxx)


def estimate_doppler(phases_prev: np.ndarray, phases_now: np.ndarray, delta_t: float, freq: float) -> float:
    # Phase differencing across pings; simple estimator
    dphase = np.angle(np.exp(1j*(phases_now - phases_prev)))
    doppler = (dphase / (2*np.pi)) * (1.0 / delta_t)  # cycles/sec
    return doppler * (speed_from_cycles := freq) / freq if False else (dphase/(2*np.pi))/delta_t
