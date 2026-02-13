# Military-Grade Sonar Display System

A professional submarine sonar console simulation built with pure HTML5, CSS3, and Canvas API.

## Features

✓ **Full-screen 100% width/height** - No margins, scrollbars, or padding  
✓ **Canvas-based rendering** - Smooth 60fps animation with requestAnimationFrame  
✓ **Realistic sonar visualization** - Circular radar with rotating sweep line  
✓ **Animated blips** - Random glowing contacts that appear and fade  
✓ **Glowing effects** - Neon green (#00ff88) with CSS box-shadow glow  
✓ **Grid and distance rings** - Nautical mile markings and bearing indicators  
✓ **Military-grade styling** - Dark navy background (#000814) with monospace text  
✓ **HUD overlays** - Real-time system status, depth, bearing, coordinates  
✓ **Noise/grain effect** - Subtle animation for realism  
✓ **Audio integration** - Automatic sonar ping sound every 1 second  
✓ **Responsive design** - Adapts to any screen size  

## How to Use

### Quick Start

1. Open `index.html` in any modern web browser
2. The sonar display will immediately start:
   - Rotating sweep line (cyan/green)
   - Random contacts appearing on screen
   - Real-time HUD data (bearing, depth, coordinates)
   - Smooth animations at 60fps

### File Structure

```
sonar_display/
├── index.html          # Main HTML file
├── sonar.css           # Styling and animations
├── sonar.js            # Canvas rendering and logic
├── audio/              # Audio files directory
│   └── sonar_ping.mp3  # (You need to add this)
└── README.md           # This file
```

## Adding Sonar Ping Audio

The sonar display is **ready for audio** but needs an MP3 file. Here's how to add it:

### Option 1: Use an Existing Sound File

1. Find or download a sonar ping sound (MP3 format)
   - Suggested: Search "sonar ping sound effect" on any sound library
   - Recommended length: 50-150ms
   - Recommended volume: Start at -3dB to -6dB

2. Save it as: `audio/sonar_ping.mp3`
   ```
   sonar_display/
   └── audio/
       └── sonar_ping.mp3  ← Place your MP3 here
   ```

3. The system will automatically play it every second!

### Option 2: Generate a Sound File Programmatically

Use this Python script to generate a synthetic sonar ping:

```python
import wave
import math

# Parameters
frequency = 10000  # Hz (sonar ping frequency)
duration = 0.1     # seconds
sample_rate = 44100  # Hz

# Generate audio data
num_samples = int(duration * sample_rate)
audio_data = []

for i in range(num_samples):
    t = i / sample_rate
    # Sine wave with envelope
    value = math.sin(2 * math.pi * frequency * t)
    # Fade envelope
    envelope = math.sin(math.pi * t / duration) ** 2
    sample = int(value * envelope * 32000)
    audio_data.append(sample)

# Save as WAV (then convert to MP3)
with wave.open('sonar_ping.wav', 'w') as wav_file:
    wav_file.setnchannels(1)  # Mono
    wav_file.setsampwidth(2)  # 16-bit
    wav_file.setframerate(sample_rate)
    
    for sample in audio_data:
        wav_file.writeframes(sample.to_bytes(2, 'little', signed=True))

# Convert to MP3 using ffmpeg:
# ffmpeg -i sonar_ping.wav -q:a 9 sonar_ping.mp3
```

Then convert the WAV to MP3 using ffmpeg:
```bash
ffmpeg -i sonar_ping.wav -q:a 9 sonar_ping.mp3
mv sonar_ping.mp3 audio/sonar_ping.mp3
```

### Option 3: Create MP3 Online

Use free online tools:
1. Go to [Bfxr](https://www.bfxr.net/) - Web-based sound effect generator
2. Set parameters for a sonar ping sound
3. Export as MP3
4. Save to `audio/sonar_ping.mp3`

### How the Audio Works

- **Location**: Sound file must be at `sonar_display/audio/sonar_ping.mp3`
- **Playback**: Automatic every 1 second (configurable via `pingInterval` in sonar.js)
- **Volume**: Set to 60% by default (adjustable in sonar.js: `this.audioElement.volume = 0.6`)
- **Error Handling**: If file not found, system continues without audio (console warning only)

## Configuration

Edit `sonar.js` to customize:

```javascript
// Sweep speed (degrees per frame)
this.sweepSpeed = 1.5;

// Range scale (nautical miles)
this.rangeScale = 10;

// Ping timing (milliseconds)
this.pingInterval = 1000;  // Every 1 second
this.pingDuration = 100;   // Animation duration

// Contact spawn rate
this.contactSpawnInterval = 3000;  // New contact every 3 seconds

// Audio volume (0.0 to 1.0)
this.audioElement.volume = 0.6;
```

## System Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- Canvas API support
- For audio: MP3 playback support

## Technical Details

### Canvas Rendering
- Uses `requestAnimationFrame` for smooth 60fps animation
- Draws dynamically: background, grid, rings, sweep line, blips
- Center-based coordinate system with radius-based layout

### Animation Pipeline
1. **Background**: Dark navy with subtle radial gradient
2. **Grid**: Distance rings (nautical miles) and bearing lines
3. **Ping animation**: Expanding circles every second
4. **Blips**: Random contacts with glow and fade effect
5. **Sweep line**: Rotating primary line with trailing glow
6. **HUD text**: Real-time updates (bearing, depth, coordinates)

### Color Scheme
- **Primary color**: #00ff88 (neon green)
- **Background**: #000814 (dark navy)
- **Accent teal**: #001428
- **Dim green**: #00bb66

### Performance Optimizations
- Delta-time based animations (frame-rate independent)
- Blip life-cycle management (auto-removal when faded)
- Efficient radius gradient rendering
- Minimal redraws using canvas clearing

## Troubleshooting

### No sound playing?
1. Check browser console for errors
2. Verify file exists: `audio/sonar_ping.mp3`
3. Check file permissions
4. Ensure not in browser's privacy/incognito mode (may mute audio)
5. Check browser volume and page audio settings

### Display looks pixelated?
- The sonar automatically scales to window size
- Resize your browser window or full-screen the page

### Animations seem choppy?
- Close other tabs/programs consuming CPU
- Update your GPU drivers
- Try a different browser

### Blips not appearing?
- They spawn randomly every 3 seconds
- Wait a few seconds for them to appear
- Check JavaScript console for errors

## Browser Compatibility

| Browser | Support |
|---------|---------|
| Chrome 90+ | ✓ Full |
| Firefox 88+ | ✓ Full |
| Safari 14+ | ✓ Full |
| Edge 90+ | ✓ Full |
| Mobile Safari | ✓ Full |
| Chrome Mobile | ✓ Full |

## Deployment

### Local Testing
```bash
# Simple HTTP server (Python 3)
python -m http.server 8000

# Or using Live Server in VS Code
# Install Live Server extension and click "Go Live"
```

### Web Server
Copy entire `sonar_display/` folder to web server:
```
www.yourserver.com/sonar_display/
```

Access via browser:
```
http://www.yourserver.com/sonar_display/index.html
```

### Important Notes
- Ensure `audio/sonar_ping.mp3` is also deployed
- Use HTTPS for production (some browsers restrict audio over HTTP)
- CORS headers should allow audio file loading

## License

This sonar display system is provided as-is for educational and entertainment purposes.

## Support

For issues or questions:
1. Check the console for error messages (F12)
2. Review the Configuration section above
3. Ensure all files are in the correct directories
4. Verify the MP3 file is valid and accessible

---

**Version**: 1.0  
**Last Updated**: 2026  
**Designed**: Military-Grade Submarine Sonar Console Simulation
