"""Beamforming implementations: delay-and-sum and MVDR (simplified).

This code contains simplified, educational implementations suitable for
simulation and research prototyping only.
"""
from __future__ import annotations
import numpy as np
from numpy.linalg import inv
from numba import njit
from typing import Tuple


def spherical_array_positions(num_elements: int, radius: float = 1.0) -> np.ndarray:
    """Place sensors approximately uniformly on a sphere (Fibonacci lattice).
    Returns array of shape (num_elements, 3).
    """
    indices = np.arange(0, num_elements, dtype=float) + 0.5
    phi = np.arccos(1 - 2*indices/num_elements)
    theta = np.pi * (1 + 5**0.5) * indices
    x = radius * np.sin(phi) * np.cos(theta)
    y = radius * np.sin(phi) * np.sin(theta)
    z = radius * np.cos(phi)
    return np.vstack((x, y, z)).T


def steering_vector(positions: np.ndarray, az_deg: float, el_deg: float, freq: float, c: float = 1500.0) -> np.ndarray:
    az = np.deg2rad(az_deg)
    el = np.deg2rad(el_deg)
    k = 2 * np.pi * freq / c
    direction = np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])
    phase_shifts = np.exp(-1j * k * (positions @ direction))
    return phase_shifts


def delay_and_sum(data: np.ndarray, positions: np.ndarray, az_deg: float, el_deg: float, fs: int, freq: float, c: float = 1500.0) -> np.ndarray:
    # data shape: (num_elements, N)
    sv = steering_vector(positions, az_deg, el_deg, freq, c)
    steered = data * sv[:, None].conjugate()
    return np.sum(steered, axis=0) / data.shape[0]


def mvdr_beamform(data: np.ndarray, positions: np.ndarray, az_deg: float, el_deg: float, freq: float, reg: float = 1e-3) -> np.ndarray:
    # Narrowband MVDR at frequency 'freq' using covariance matrix approach (simplified)
    # data: (num_elements, N) -> take one frequency bin via FFT for demonstration
    X = np.fft.fft(data, axis=1)
    bin_idx = int(freq / (data.shape[1])) if data.shape[1] > 0 else 0
    snapshot = X[:, bin_idx:bin_idx+1]
    R = snapshot @ snapshot.conj().T
    R += reg * np.eye(R.shape[0])
    sv = steering_vector(positions, az_deg, el_deg, freq)
    w = inv(R) @ sv
    w = w / (sv.conj().T @ inv(R) @ sv)
    return (w.conj().T @ data).ravel()
