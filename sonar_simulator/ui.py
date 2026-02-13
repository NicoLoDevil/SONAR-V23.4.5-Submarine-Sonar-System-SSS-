"""Visualization and simple UI for the sonar simulator.

Provides a Matplotlib-based real-time dashboard with spectrogram and polar
bearing plot. Plays a chirp ping sound each cycle (simulation-only).
"""
from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
import threading
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def play_sound(sig: np.ndarray, fs: int = 44100):
    try:
        import sounddevice as sd
        sd.play(sig, fs)
        sd.wait()
    except Exception:
        try:
            import pyaudio
            pa = pyaudio.PyAudio()
            stream = pa.open(format=pyaudio.paFloat32, channels=1, rate=fs, output=True)
            stream.write(sig.astype('float32').tobytes())
            stream.stop_stream()
            stream.close()
            pa.terminate()
        except Exception as e:
            logger.warning('No audio backend available: %s', e)


class SonarUI:
    def __init__(self, sample_rate: int = 44100, headless: bool = False, outdir: str | None = None):
        self.sample_rate = sample_rate
        self.headless = headless
        self.outdir = outdir
        if headless:
            import matplotlib
            matplotlib.use('Agg')
        else:
            plt.ion()
        self.fig = plt.figure(figsize=(10, 6))
        self.ax_spec = self.fig.add_subplot(2, 2, 1)
        self.ax_polar = self.fig.add_subplot(2, 2, 2, projection='polar')
        self.ax_bti = self.fig.add_subplot(2, 1, 2)
        self._frame_idx = 0

    def update_spectrogram(self, signal: np.ndarray):
        self.ax_spec.clear()
        self.ax_spec.specgram(signal, NFFT=1024, Fs=self.sample_rate, noverlap=512)
        self.ax_spec.set_title('Spectrogram')

    def update_bearing(self, bearings: np.ndarray, mags: np.ndarray):
        self.ax_polar.clear()
        thetas = np.deg2rad(bearings)
        self.ax_polar.scatter(thetas, mags)
        self.ax_polar.set_title('Bearing plot')

    def update_bti(self, times: np.ndarray, bearings: np.ndarray, mags: np.ndarray):
        self.ax_bti.clear()
        sc = self.ax_bti.scatter(times, bearings, c=mags, cmap='viridis')
        self.ax_bti.set_ylabel('Bearing (deg)')
        self.ax_bti.set_xlabel('Time (s)')
        self.fig.colorbar(sc, ax=self.ax_bti, label='Intensity')

    def show(self):
        if self.headless and self.outdir is not None:
            path = f"{self.outdir}/frame_{self._frame_idx:04d}.png"
            self.fig.savefig(path)
            self._frame_idx += 1
        else:
            plt.draw()
            plt.pause(0.001)
