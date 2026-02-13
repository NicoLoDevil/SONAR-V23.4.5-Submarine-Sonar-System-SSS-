#!/usr/bin/env python3
"""
Sonar Ping Sound Generator
Generates a realistic sonar ping sound and saves as MP3.

This script creates a synthetic sonar ping sound with:
- High-frequency sine wave (10 kHz)
- Realistic fade envelope
- Professional audio quality
"""

import wave
import struct
import math
import sys
import os
import subprocess

def generate_sonar_ping(output_file='sonar_ping.wav', frequency=10000, duration=0.15, sample_rate=44100):
    """
    Generate a sonar ping sound.
    
    Args:
        output_file: Output WAV file path
        frequency: Frequency in Hz (default 10000 Hz / 10 kHz)
        duration: Duration in seconds (default 0.15 seconds)
        sample_rate: Sample rate in Hz (default 44100 Hz / CD quality)
    """
    
    print(f"Generating sonar ping sound...")
    print(f"  Frequency: {frequency} Hz")
    print(f"  Duration: {duration} seconds")
    print(f"  Sample rate: {sample_rate} Hz")
    
    # Calculate number of samples
    num_samples = int(duration * sample_rate)
    
    # Generate audio data
    audio_data = []
    
    for i in range(num_samples):
        t = i / sample_rate
        
        # Sine wave oscillation
        oscillation = math.sin(2 * math.pi * frequency * t)
        
        # Fade envelope (swell and fade)
        # Rising part (first 30%)
        if t < duration * 0.3:
            envelope = (t / (duration * 0.3)) ** 1.5
        # Sustained part (middle 40%)
        elif t < duration * 0.7:
            envelope = 1.0
        # Fading part (last 30%)
        else:
            envelope = ((duration - t) / (duration * 0.3)) ** 1.5
        
        # Combine oscillation and envelope
        sample_value = oscillation * envelope
        
        # Add slight harmonic for realism (high frequency whistle)
        harmonic = math.sin(2 * math.pi * frequency * 2.5 * t) * envelope * 0.15
        sample_value += harmonic
        
        # Convert to 16-bit audio sample (-32768 to 32767)
        sample_16bit = int(sample_value * 32000)
        
        # Clamp to valid range
        sample_16bit = max(-32768, min(32767, sample_16bit))
        audio_data.append(sample_16bit)
    
    # Write to WAV file
    with wave.open(output_file, 'w') as wav_file:
        # Parameters: channels, sample width (bytes), sample rate
        wav_file.setnchannels(1)      # Mono
        wav_file.setsampwidth(2)      # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Write audio data
        for sample in audio_data:
            wav_file.writeframes(struct.pack('<h', sample))
    
    print(f"✓ WAV file created: {output_file}")
    return output_file

def convert_to_mp3(wav_file, mp3_file=None):
    """
    Convert WAV file to MP3 using ffmpeg.
    
    Args:
        wav_file: Input WAV file path
        mp3_file: Output MP3 file path (defaults to same name with .mp3)
    """
    
    if mp3_file is None:
        mp3_file = os.path.splitext(wav_file)[0] + '.mp3'
    
    # Check if ffmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("✗ ffmpeg not found. Install it to convert to MP3:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return None
    
    print(f"\nConverting to MP3...")
    print(f"  Input: {wav_file}")
    print(f"  Output: {mp3_file}")
    
    try:
        # Convert WAV to MP3 with good quality
        subprocess.run([
            'ffmpeg',
            '-i', wav_file,
            '-q:a', '2',      # High quality (2 is best)
            '-codec:a', 'libmp3lame',
            '-b:a', '192k',   # 192 kbps bitrate
            mp3_file,
            '-y',             # Overwrite output file
            '-loglevel', 'error'  # Only show errors
        ], check=True)
        
        print(f"✓ MP3 file created: {mp3_file}")
        return mp3_file
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error during conversion: {e}")
        return None

def main():
    """Main script execution."""
    
    # Check if we're in the sonar_display directory
    current_dir = os.getcwd()
    audio_dir = os.path.join(current_dir, 'audio')
    
    # Create audio directory if it doesn't exist
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
        print(f"Created directory: {audio_dir}")
    
    # Set output paths
    wav_file = os.path.join(audio_dir, 'sonar_ping.wav')
    mp3_file = os.path.join(audio_dir, 'sonar_ping.mp3')
    
    print("=" * 60)
    print("SONAR PING SOUND GENERATOR")
    print("=" * 60)
    
    # Generate WAV file
    generate_sonar_ping(wav_file)
    
    # Try to convert to MP3
    result = convert_to_mp3(wav_file, mp3_file)
    
    print("\n" + "=" * 60)
    if result:
        print("✓ SUCCESS! Sonar ping sound generated and converted to MP3")
        print(f"\nFile location: {mp3_file}")
        print("\nThe sonar display will now automatically play this sound")
        print("every second when you open index.html in your browser.")
        
        # Optionally clean up WAV file
        try:
            os.remove(wav_file)
            print(f"\nCleaned up temporary WAV file")
        except:
            print(f"\nKeeping WAV file: {wav_file}")
    else:
        print("⚠ WAV file created but couldn't convert to MP3")
        print(f"\nYou can:")
        print(f"1. Convert manually: ffmpeg -i {wav_file} -q:a 2 {mp3_file}")
        print(f"2. Or use the WAV file directly (supported by modern browsers)")
        print(f"\nCopy {wav_file} to {mp3_file} to use it")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
