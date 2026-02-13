import numpy as np
from sonar_simulator.input import SonarInput


def test_chirp_length():
    si = SonarInput()
    sig = si.generate_chirp(f0=2000, f1=8000, duration=0.2)
    assert len(sig) == int(si.sample_rate * 0.2)


def test_array_ping_delay():
    si = SonarInput()
    chirp = si.generate_chirp(duration=0.1)
    ranges = {0: 1500.0}  # 1500 m -> delay ~2s round trip
    arr = si.make_array_ping(chirp, ranges, speed_of_sound=1500.0)
    # ensure energy in expected delayed region (check absolute energy)
    delay_samples = int((2 * 1500.0 / 1500.0) * si.sample_rate)
    assert arr.shape[0] == si.channels
    assert np.abs(arr[0, delay_samples:delay_samples+10]).max() > 0
