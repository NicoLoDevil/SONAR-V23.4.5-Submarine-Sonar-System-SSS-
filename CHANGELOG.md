# Changelog

All notable changes to the SONAR Submarine Sonar System will be documented in this file.

## [Unreleased]

### Added
- Audio device detection: Automatically detects connected speakers and microphone using Web Audio API
- Audio device status panel in right-side HUD showing real-time speaker and mic status (ACTIVE/OFFLINE/CHECKING)
- Changelog tracking system for all future updates and modifications
- Automatic hardware capability checks on page load with error handling

### Changed
- Right-center HUD panel now combines audio device detection with Missing Misc components

### Removed
- None

### Fixed
- None

---

## [1.1.0] - 2026-02-13

### Added
- Realistic sonar startup: All stats (depth, temperature, signal strength, frequency variance) initialize to 0
- Progressive stat increases: Depth and stats increase with each ping cycle with random variance
- GPS-based speed calculation: Speed (knots) only updates when actual GPS movement detected
- Ping counter tracking

### Changed
- Initial depth changed from 185m to 0m for realism
- Initial temperature changed from 12°C to 0°C
- Depth and temperature now increase progressively rather than remaining static

---

## [1.0.0] - 2026-02-05

### Added
- Complete military-grade submarine sonar display console
- Canvas-based real-time sonar visualization at 60fps
- Rotating 360° sweep line with glow effects (0.5°/frame)
- Concentric distance rings (nautical mile markers)
- Dark navy background with phosphorescent green (#00ff88) HUD elements
- Random contact blips with spawning/fading lifecycle (8-second intervals)
- 6 HUD panels: System Status, Vessel Data, Range, Position, Contacts, Missing Misc
- Audio integration with sonar_ping.mp3 (207KB, 5.28s duration)
- Audio/visual ping perfect synchronization (audio 'play'/'ended' events)
- Device motion integration (gyroscope compass bearing, tilt-based depth)
- Geolocation tracking (GPS coordinates with high accuracy)
- Bearing, depth, coordinates, temperature real-time display
- Monospaced technical font (Courier New) for authentic military feel
- Text shadows and glow effects for phosphor screen simulation
- Responsive layout for mobile and desktop devices
- Full-screen 100% width/height with no scrollbars

### Technology
- HTML5 Canvas API for rendering
- Web Audio API integration
- DeviceOrientationEvent API for compass
- Geolocation API for GPS
- JavaScript ES6+ with requestAnimationFrame loops
- CSS3 animations and gradients

---
