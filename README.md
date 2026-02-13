# Sonar Simulator (simulation-only)

This repository contains a Python-based sonar simulator inspired by public,
unclassified descriptions of BQQ-6 and BQQ-10 sonar suites. It is strictly a
software simulation and must not be used for real sonar hardware or classified
systems. Use for research, teaching, or proof-of-concept AI experiments.

Features:
- Synthetic LFM chirp generation and playback
- Multi-element spherical array simulation (102 elements)
- Delay-and-sum beamforming + simplified MVDR stub
- Matched filtering and a simple CFAR detector
- Basic Kalman tracker and SVM classifier stub
- Matplotlib UI: spectrogram, polar bearing plot, BTI
- Basic ocean propagation models (spreading, multipath, ambient noise)

Run (in Codespace or local machine):

```bash
python -m sonar_simulator.main
```

Dependencies are listed in `requirements.txt`. In environments where `pyaudio`
is not available, the simulator will try `sounddevice` as a fallback.

Mathematics:
- Range estimate (one-way): $range = c \cdot delay$; for active sonar two-way: $range = (c \cdot delay)/2$
- Steering vector: $a(\theta)=e^{-j k r \cdot \hat{u}(\theta)}$ where $k=2\pi f / c$.

Limitations and ethics:
- This code is deliberately simplified for learning and prototyping. It is
  not suitable for deployment or real-world sonar operations.
- Do not use this to control or interface with actual naval systems.
# Plans
I plan to make this software for the (Ohio-Class) submarine to use. This project is still in development and will not be finished until around A month or so. This software has yet to come. All additional features will come out soon for the new Sonar Ping Software (SPS)

# Versions
23.4.5 will be ONE of the best sonar GUI/UI designs and MORE!.
23.4.4 was ONE of the best UI/GUI and SONAR Frequency (htz) designs/sounds.

# Notice
If you want to download and use this software, you need a REAL Sonar Pinging Machine. You can't legally own one. 
I am not legally required to upload this software, but I want to share it with you guys so you can explore and see what goes on!

# Extra
- Nothing here.
