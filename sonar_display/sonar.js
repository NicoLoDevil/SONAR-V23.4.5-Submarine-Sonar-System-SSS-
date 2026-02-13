/**
 * Military-Grade Sonar Display System
 * Canvas-based real-time sonar visualization
 */

class SonarDisplay {
    constructor() {
        this.canvas = document.getElementById('sonarCanvas');
        this.ctx = this.canvas.getContext('2d');
        
        // Ensure canvas fills entire window
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
        
        // Center of sonar display
        this.centerX = this.canvas.width / 2;
        this.centerY = this.canvas.height / 2;
        this.maxRadius = Math.min(this.centerX, this.centerY) * 0.85;
        
        // Sonar parameters
        this.sweepAngle = 0;
        this.sweepSpeed = 0.5; // degrees per frame (slowed down)
        this.rangeScale = 10; // nautical miles
        this.pixelsPerNauticalMile = this.maxRadius / this.rangeScale;
        
        // Blips (contacts)
        this.blips = [];
        this.contactCount = 0;
        this.lastContactTime = 0;
        this.contactSpawnInterval = 8000; // ms between new contacts (RARE - 8 seconds)
        
        // Ping timing
        this.lastPingTime = 0;
        this.pingInterval = 10000; // 10 seconds (matches sonar sweep cycle)
        this.pingDuration = 100; // animation duration
        this.pingProgress = 0;
        this.audioDuration = 5280; // milliseconds (from audio file duration)
        this.audioStartTime = 0; // track when audio starts playing
        this.syncedPingTriggered = false; // track ping sync state
        
        // Animation
        this.lastTime = Date.now();
        this.frameCount = 0;
        
        // Audio
        this.audioElement = document.getElementById('sonarPing');
        this.setupAudio();
        
        // Device Motion & Geolocation
        this.currentDepth = 0; // Start at 0 (realistic)
        this.currentBearing = 0; // degrees
        this.currentLatitude = 42 + 35/60 + 24/3600; // Base coordinates
        this.currentLongitude = -(71 + 2/60 + 18/3600);
        this.currentTemperature = 0; // Start at 0
        this.currentSpeed = 0; // Knots - only updates with real GPS movement
        
        // Track GPS for speed calculation
        this.lastLatitude = this.currentLatitude;
        this.lastLongitude = this.currentLongitude;
        this.lastPositionTime = Date.now();
        
        // Stats that increase with each ping
        this.pingCount = 0;
        this.signalStrength = 0;
        this.frequencyVariance = 0;
        
        // Audio Device Detection
        this.speakerStatus = 'OFFLINE';
        this.micStatus = 'OFFLINE';
        
        this.setupDeviceMotion();
        this.setupGeolocation();
        this.checkAudioDevices();
        
        // Start animation loop
        this.animate();
    }
    
    setupAudio() {
        // Check if audio file exists
        const audioPath = 'audio/sonar_ping.mp3';
        this.audioElement.src = audioPath;
        this.audioElement.volume = 0.6;
        this.audioIsPlaying = false;
        
        // Track when audio starts - trigger immediate ping
        this.audioElement.addEventListener('play', () => {
            this.audioStartTime = Date.now();
            this.audioIsPlaying = true;
            this.syncedPingTriggered = false;
            // Trigger ping at start of audio
            this.lastPingTime = Date.now();
            this.pingProgress = 0;
        });
        
        // Track when audio ends - trigger final ping
        this.audioElement.addEventListener('ended', () => {
            this.audioIsPlaying = false;
            // Trigger ping at end of audio
            this.lastPingTime = Date.now();
            this.pingProgress = 0;
        });
        
        // Handle audio loading errors gracefully
        this.audioElement.addEventListener('error', () => {
            this.audioIsPlaying = false;
            console.warn('Sonar ping audio file not found. To add sound:');
            console.warn('1. Place an MP3 file at: sonar_display/audio/sonar_ping.mp3');
            console.warn('2. The sound will play automatically every 10 seconds during operation');
        });
    }
    
    playPingSound() {
        try {
            // Only play if not already playing (prevents interruption)
            if (!this.audioIsPlaying) {
                this.audioElement.currentTime = 0;
                this.audioElement.play();
            }
        } catch (e) {
            // Silently fail if audio not available
        }
    }
    
    checkAudioDevices() {
        // Check for microphone and speakers
        navigator.mediaDevices.enumerateDevices()
            .then(devices => {
                let hasMicrophone = false;
                let hasSpeaker = false;
                
                devices.forEach(device => {
                    if (device.kind === 'audioinput') {
                        hasMicrophone = true;
                    }
                    if (device.kind === 'audiooutput') {
                        hasSpeaker = true;
                    }
                });
                
                // Update status
                this.speakerStatus = hasSpeaker ? 'ACTIVE' : 'OFFLINE';
                this.micStatus = hasMicrophone ? 'ACTIVE' : 'OFFLINE';
                
                // Update HUD display
                this.updateDeviceStatus();
                
                console.log(`Audio Devices - Speaker: ${this.speakerStatus}, Mic: ${this.micStatus}`);
            })
            .catch(err => {
                console.warn('Could not enumerate audio devices:', err.message);
                this.speakerStatus = 'UNKNOWN';
                this.micStatus = 'UNKNOWN';
                this.updateDeviceStatus();
            });
    }
    
    updateDeviceStatus() {
        // Update speaker status in HUD
        const speakerStatus = document.getElementById('speakerStatus');
        if (speakerStatus) {
            speakerStatus.textContent = this.speakerStatus;
            speakerStatus.className = this.speakerStatus === 'ACTIVE' ? 'status-active' : 'status-warning';
        }
        
        // Update microphone status in HUD
        const micStatus = document.getElementById('micStatus');
        if (micStatus) {
            micStatus.textContent = this.micStatus;
            micStatus.className = this.micStatus === 'ACTIVE' ? 'status-active' : 'status-warning';
        }
    }
    
    setupDeviceMotion() {
        // Request permission for device orientation (iOS 13+)
        if (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function') {
            // iOS 13+ requires user gesture
            window.addEventListener('click', () => {
                DeviceOrientationEvent.requestPermission()
                    .then(permissionState => {
                        if (permissionState === 'granted') {
                            this.enableDeviceOrientation();
                        }
                    })
                    .catch(console.error);
            }, { once: true });
        } else if (typeof DeviceOrientationEvent !== 'undefined') {
            // Non-iOS devices
            this.enableDeviceOrientation();
        }
    }
    
    enableDeviceOrientation() {
        window.addEventListener('deviceorientation', (event) => {
            // Alpha: rotation around z-axis (0-360)
            // Beta: rotation around x-axis (-180 to 180)
            // Gamma: rotation around y-axis (-90 to 90)
            
            const alpha = event.alpha || 0; // Compass heading
            const beta = event.beta || 0;
            const gamma = event.gamma || 0;
            
            // Update bearing based on compass (alpha)
            this.currentBearing = Math.floor(alpha);
            
            // Update depth based on tilt (beta)
            // Tilting forward decreases depth, tilting back increases depth
            const depthVariance = Math.floor((beta / 180) * 50); // ±50 meters
            this.currentDepth = 185 + depthVariance;
            
            // Update temperature based on rotation (gamma)
            const tempVariance = (gamma / 90) * 3; // ±3 degrees
            this.currentTemperature = 12 + tempVariance;
        });
    }
    
    setupGeolocation() {
        // Request geolocation permission
        if ('geolocation' in navigator) {
            navigator.geolocation.watchPosition(
                (position) => {
                    const now = Date.now();
                    const timeDelta = (now - this.lastPositionTime) / 1000; // seconds
                    
                    // Calculate distance moved (rough haversine)
                    const dLat = position.coords.latitude - this.lastLatitude;
                    const dLon = position.coords.longitude - this.lastLongitude;
                    const distance = Math.sqrt(dLat * dLat + dLon * dLon) * 69; // rough miles conversion
                    
                    // Calculate speed in knots (only if actually moved)
                    if (timeDelta > 0 && distance > 0.001) {
                        this.currentSpeed = (distance / timeDelta) * 0.868; // convert to knots
                    } else {
                        this.currentSpeed = 0; // No movement = 0 knots
                    }
                    
                    // Update coordinates
                    this.currentLatitude = position.coords.latitude;
                    this.currentLongitude = position.coords.longitude;
                    this.lastLatitude = position.coords.latitude;
                    this.lastLongitude = position.coords.longitude;
                    this.lastPositionTime = now;
                },
                (error) => {
                    console.warn('Geolocation error:', error.message);
                    this.currentSpeed = 0; // No GPS = 0 knots
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 5000
                }
            );
        }
    }
    
    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.centerX = this.canvas.width / 2;
        this.centerY = this.canvas.height / 2;
        this.maxRadius = Math.min(this.centerX, this.centerY) * 0.85;
        this.pixelsPerNauticalMile = this.maxRadius / this.rangeScale;
    }
    
    drawNoiseGrain(alpha = 0.03) {
        const imageData = this.ctx.createImageData(this.canvas.width, this.canvas.height);
        const data = imageData.data;
        
        for (let i = 0; i < data.length; i += 4) {
            const noise = Math.random() * 255;
            data[i] = noise;
            data[i + 1] = noise * 0.5;
            data[i + 2] = noise * 0.3;
            data[i + 3] = alpha * 255;
        }
        
        this.ctx.putImageData(imageData, 0, 0);
    }
    
    drawBackground() {
        // Dark navy background
        this.ctx.fillStyle = '#000814';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Subtle background gradient
        const gradient = this.ctx.createRadialGradient(
            this.centerX, this.centerY, 0,
            this.centerX, this.centerY, this.maxRadius
        );
        gradient.addColorStop(0, 'rgba(0, 30, 60, 0.1)');
        gradient.addColorStop(1, 'rgba(0, 8, 20, 0.3)');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Add subtle noise
        this.drawNoiseGrain(0.02);
    }
    
    drawGridAndRings() {
        // Distance rings (nautical miles)
        const ringCount = 5;
        
        for (let i = 1; i <= ringCount; i++) {
            const radius = (this.maxRadius / ringCount) * i;
            
            // Ring circle
            this.ctx.strokeStyle = `rgba(0, 255, 136, ${0.15 - i * 0.02})`;
            this.ctx.lineWidth = 1;
            this.ctx.beginPath();
            this.ctx.arc(this.centerX, this.centerY, radius, 0, Math.PI * 2);
            this.ctx.stroke();
            
            // Glowing ring effect
            this.ctx.strokeStyle = `rgba(0, 255, 136, ${0.08 - i * 0.01})`;
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.arc(this.centerX, this.centerY, radius, 0, Math.PI * 2);
            this.ctx.stroke();
            
            // Distance labels on N, E, S, W
            const distance = i * this.rangeScale;
            this.ctx.fillStyle = 'rgba(0, 200, 136, 0.6)';
            this.ctx.font = 'bold 11px Courier New';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            
            // North label
            this.ctx.fillText(`${distance}nm`, this.centerX, this.centerY - radius - 12);
        }
        
        // Radial grid lines (bearings)
        const bearingCount = 12; // Every 30 degrees
        this.ctx.strokeStyle = 'rgba(0, 255, 136, 0.1)';
        this.ctx.lineWidth = 1;
        
        for (let i = 0; i < bearingCount; i++) {
            const angle = (i / bearingCount) * Math.PI * 2;
            const x = this.centerX + Math.cos(angle) * this.maxRadius;
            const y = this.centerY + Math.sin(angle) * this.maxRadius;
            
            this.ctx.beginPath();
            this.ctx.moveTo(this.centerX, this.centerY);
            this.ctx.lineTo(x, y);
            this.ctx.stroke();
        }
        
        // Cardinal direction labels
        const directions = [
            { label: 'N', angle: -Math.PI / 2 },
            { label: 'E', angle: 0 },
            { label: 'S', angle: Math.PI / 2 },
            { label: 'W', angle: Math.PI }
        ];
        
        this.ctx.fillStyle = '#00ff88';
        this.ctx.font = 'bold 14px Courier New';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        
        directions.forEach(dir => {
            const x = this.centerX + Math.cos(dir.angle) * (this.maxRadius + 35);
            const y = this.centerY + Math.sin(dir.angle) * (this.maxRadius + 35);
            this.ctx.fillText(dir.label, x, y);
        });
    }
    
    updateBlips(deltaTime) {
        // Update existing blips
        this.blips = this.blips.filter(blip => {
            blip.age += deltaTime;
            blip.alpha = Math.max(0, 1 - (blip.age / blip.lifetime));
            return blip.alpha > 0;
        });
        
        // Spawn new random blips
        const now = Date.now();
        if (now - this.lastContactTime > this.contactSpawnInterval) {
            // Random angle and distance
            const angle = Math.random() * Math.PI * 2;
            const distance = Math.random() * this.maxRadius * 0.95;
            const x = this.centerX + Math.cos(angle) * distance;
            const y = this.centerY + Math.sin(angle) * distance;
            
            // Random bearing for display
            const bearing = Math.floor((angle * 180 / Math.PI + 90) % 360);
            const range = (distance / this.pixelsPerNauticalMile).toFixed(1);
            
            this.blips.push({
                x: x,
                y: y,
                angle: angle,
                distance: distance,
                age: 0,
                lifetime: 4000 + Math.random() * 3000,
                alpha: 1,
                size: 2 + Math.random() * 3,
                bearing: bearing,
                range: range,
                id: ++this.contactCount
            });
            
            this.lastContactTime = now;
        }
        
        // Update contact count in UI
        document.getElementById('contactCount').textContent = this.blips.length;
        
        // Update contacts list
        this.updateContactsList();
    }
    
    updateContactsList() {
        const contactsList = document.getElementById('contactsList');
        const topContacts = this.blips
            .sort((a, b) => a.distance - b.distance)
            .slice(0, 5);
        
        contactsList.innerHTML = topContacts
            .map(c => `<div class="contact-item">BRG:${c.bearing}° RNG:${c.range}nm</div>`)
            .join('');
    }
    
    drawBlips() {
        this.blips.forEach(blip => {
            // Main blip glow
            const gradient = this.ctx.createRadialGradient(
                blip.x, blip.y, 0,
                blip.x, blip.y, blip.size * 8
            );
            gradient.addColorStop(0, `rgba(0, 255, 136, ${blip.alpha * 0.8})`);
            gradient.addColorStop(0.5, `rgba(0, 200, 100, ${blip.alpha * 0.3})`);
            gradient.addColorStop(1, `rgba(0, 100, 80, 0)`);
            
            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(blip.x, blip.y, blip.size * 8, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Core blip
            this.ctx.fillStyle = `rgba(0, 255, 136, ${blip.alpha})`;
            this.ctx.beginPath();
            this.ctx.arc(blip.x, blip.y, blip.size, 0, Math.PI * 2);
            this.ctx.fill();
        });
    }
    
    drawSweepLine() {
        const sweepRadians = (this.sweepAngle * Math.PI) / 180;
        const endX = this.centerX + Math.cos(sweepRadians) * this.maxRadius;
        const endY = this.centerY + Math.sin(sweepRadians) * this.maxRadius;
        
        // Bright sweep line
        this.ctx.strokeStyle = '#00ff88';
        this.ctx.lineWidth = 2;
        this.ctx.lineCap = 'round';
        this.ctx.beginPath();
        this.ctx.moveTo(this.centerX, this.centerY);
        this.ctx.lineTo(endX, endY);
        this.ctx.stroke();
        
        // Glow effect - trailing sweep
        const trailLength = 30; // degrees
        for (let i = 1; i <= trailLength; i++) {
            const trailAngle = (this.sweepAngle - i) * Math.PI / 180;
            const alpha = Math.max(0, (trailLength - i) / trailLength) * 0.3;
            
            const x = this.centerX + Math.cos(trailAngle) * this.maxRadius;
            const y = this.centerY + Math.sin(trailAngle) * this.maxRadius;
            
            this.ctx.strokeStyle = `rgba(0, 255, 136, ${alpha})`;
            this.ctx.lineWidth = 1;
            this.ctx.beginPath();
            this.ctx.moveTo(this.centerX, this.centerY);
            this.ctx.lineTo(x, y);
            this.ctx.stroke();
        }
        
        // Center circle
        this.ctx.fillStyle = '#00ff88';
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY, 4, 0, Math.PI * 2);
        this.ctx.fill();
    }
    
    drawPingAnimation() {
        const now = Date.now();
        if (now - this.lastPingTime > this.pingInterval) {
            this.lastPingTime = now;
            this.pingProgress = 0;
            this.playPingSound();
            
            // Update stats with each ping
            this.updateStats();
        }
        
        // Draw expanding ping ring
        if (Date.now() - this.lastPingTime < this.pingDuration) {
            const progress = (Date.now() - this.lastPingTime) / this.pingDuration;
            const radius = this.maxRadius * progress;
            const alpha = 1 - progress;
            
            this.ctx.strokeStyle = `rgba(0, 255, 136, ${alpha * 0.8})`;
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.arc(this.centerX, this.centerY, radius, 0, Math.PI * 2);
            this.ctx.stroke();
            
            // Outer glow ring
            this.ctx.strokeStyle = `rgba(0, 255, 136, ${alpha * 0.3})`;
            this.ctx.lineWidth = 4;
            this.ctx.beginPath();
            this.ctx.arc(this.centerX, this.centerY, radius, 0, Math.PI * 2);
            this.ctx.stroke();
        }
    }
    
    updateStats() {
        // Increment ping count
        this.pingCount++;
        
        // Progressive depth increase (max 185m, ~2m per ping starting early)
        if (this.currentDepth < 185) {
            this.currentDepth += (2 + Math.random() * 3); // 2-5m per ping
        }
        
        // Progressive signal strength increase (0-100 with variance)
        const strengthIncrease = 3 + Math.random() * 4; // 3-7 per ping
        this.signalStrength = Math.min(100, this.signalStrength + strengthIncrease);
        // Add random variance (-10 to +10)
        this.signalStrength = Math.max(0, Math.min(100, 
            this.signalStrength + (Math.random() * 20 - 10)
        ));
        
        // Progressive frequency variance (increases with noise)
        const freqVariance = 1 + Math.random() * 2; // 1-3 Hz per ping
        this.frequencyVariance = Math.min(5, this.frequencyVariance + freqVariance);
        // Add random variance (-1 to +1)
        this.frequencyVariance = Math.max(0, Math.min(5,
            this.frequencyVariance + (Math.random() * 2 - 1)
        ));
    }
    
    updateSweep() {
        this.sweepAngle += this.sweepSpeed;
        if (this.sweepAngle >= 360) {
            this.sweepAngle = 0;
        }
    }
    
    updateBearing() {
        // Update bearing from device orientation (real compass heading)
        // No longer tied to sweep animation
        document.getElementById('bearing').textContent = String(this.currentBearing).padStart(3, '0') + '°';
        
        // Update depth from device tilt
        document.getElementById('ownDepth').textContent = Math.floor(this.currentDepth) + ' m';
        
        // Update speed from GPS movement (only non-zero if actually moving)
        document.getElementById('currentSpeed').textContent = this.currentSpeed.toFixed(1) + ' knots';
        
        // Update coordinates from geolocation
        const latDeg = Math.floor(this.currentLatitude);
        const latMin = Math.floor((this.currentLatitude % 1) * 60);
        const latSec = Math.floor(((this.currentLatitude % 1) * 60 % 1) * 60);
        const latStr = `${latDeg}°${latMin}'${latSec}"N`;
        
        const lonDeg = Math.floor(Math.abs(this.currentLongitude));
        const lonMin = Math.floor((Math.abs(this.currentLongitude) % 1) * 60);
        const lonSec = Math.floor(((Math.abs(this.currentLongitude) % 1) * 60 % 1) * 60);
        const lonStr = `${lonDeg}°${lonMin}'${lonSec}"W`;
        
        document.getElementById('latitude').textContent = latStr;
        document.getElementById('longitude').textContent = lonStr;
    }
    
    updateFrequency() {
        // Update frequency display with variance
        const baseFreq = 37.5;
        const freq = baseFreq + this.frequencyVariance;
        document.getElementById('frequency').textContent = freq.toFixed(2) + ' kHz';
        
        // Update signal strength display
        document.getElementById('signalStrength').textContent = Math.floor(this.signalStrength) + '%';
    }
    
    animate() {
        const now = Date.now();
        const deltaTime = Math.min(16, now - this.lastTime); // Cap at 60fps
        this.lastTime = now;
        
        // Clear and redraw
        this.drawBackground();
        this.drawGridAndRings();
        this.drawPingAnimation();
        this.updateBlips(deltaTime);
        this.drawBlips();
        this.drawSweepLine();
        this.updateSweep();
        
        // Update UI less frequently (not every frame)
        if (this.frameCount % 10 === 0) {
            this.updateBearing();
            this.updateFrequency();
        }
        
        this.frameCount++;
        
        // Continue animation loop
        requestAnimationFrame(() => this.animate());
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new SonarDisplay();
});
