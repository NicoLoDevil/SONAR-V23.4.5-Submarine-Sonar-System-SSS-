"""Target tracker and simple classifier.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any
from sklearn.svm import SVC


@dataclass
class Track:
    id: int
    state: np.ndarray  # [x, y, vx, vy]
    P: np.ndarray


class TargetTracker:
    def __init__(self, max_tracks: int = 10):
        self.tracks: Dict[int, Track] = {}
        self.next_id = 1

    def predict(self, dt: float):
        for tr in self.tracks.values():
            F = np.array([[1, 0, dt, 0], [0, 1, 0, dt], [0, 0, 1, 0], [0, 0, 0, 1]])
            tr.state = F @ tr.state
            tr.P = F @ tr.P @ F.T + np.eye(4) * 0.1

    def update(self, detections: List[np.ndarray]):
        # Very simple nearest-neighbor assignment
        for d in detections:
            if not self.tracks:
                self.tracks[self.next_id] = Track(self.next_id, np.array([d[0], d[1], 0.0, 0.0]), np.eye(4))
                self.next_id += 1
                continue
            # find nearest
            best_id = None
            best_dist = float('inf')
            for tid, tr in self.tracks.items():
                dist = np.linalg.norm(tr.state[:2] - d[:2])
                if dist < best_dist:
                    best_dist = dist
                    best_id = tid
            if best_dist < 1000:  # meters threshold
                tr = self.tracks[best_id]
                z = np.array([d[0], d[1]])
                H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])
                y = z - H @ tr.state
                S = H @ tr.P @ H.T + np.eye(2) * 10
                K = tr.P @ H.T @ np.linalg.inv(S)
                tr.state = tr.state + K @ y
                tr.P = (np.eye(4) - K @ H) @ tr.P
            else:
                self.tracks[self.next_id] = Track(self.next_id, np.array([d[0], d[1], 0.0, 0.0]), np.eye(4))
                self.next_id += 1


class SimpleClassifier:
    def __init__(self):
        self.model = SVC(probability=True)
        self.trained = False

    def featurize(self, spectrum: np.ndarray) -> np.ndarray:
        # Very simple feature vector: banded energy
        bands = np.array_split(np.abs(spectrum), 8)
        return np.array([b.mean() for b in bands])

    def train(self, X: np.ndarray, y: np.ndarray):
        self.model.fit(X, y)
        self.trained = True

    def predict(self, spectrum: np.ndarray) -> Any:
        if not self.trained:
            return 'unknown'
        feat = self.featurize(spectrum).reshape(1, -1)
        return self.model.predict(feat)[0]
