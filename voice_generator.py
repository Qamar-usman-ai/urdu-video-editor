# voice_generator.py
import soundfile as sf
import numpy as np
from scipy import signal
import os
import tempfile

class VoiceGenerator:
    """Handles text-to-speech conversion with Urdu support"""
    
    def __init__(self):
        """Initialize text-to-speech engine"""
        self.sample_rate = 44100
        self.use_gtts = True
        self.available = self._check_availability()
    
    def _check_availability(self):
        """Check if gTTS is available"""
        try:
            from gtts import gTTS
            return True
        except ImportError:
            print("Warning: gTTS not installed. Voice generation will be limited.")
            return False
    
    def generate_voice(self, text, output_path, speed=1.0, pitch=1.0):
        """
        Generate voice-over from Urdu text using gTTS
        
        Args:
            text: Urdu text to convert to speech
            output_path: Path to save audio file
            speed: Speech speed (0.5-2.0, default 1.0)
            pitch: Pitch level (0.5-2.0, default 1.0)
            
        Returns:
            bool: Success status
        """
        try:
            # Use gTTS for Urdu text-to-speech
            if self.use_gtts and self.available:
                return self._generate_with_gtts(text, output_path, speed)
            else:
                return self._generate_fallback(text, output_path)
            
        except Exception as e:
            print(f"Error generating voice: {str(e)}")
            return False
    
    def _generate_with_gtts(self, text, output_path, speed=1.0):
        """
        Generate voice using Google Text-to-Speech
        
        Args:
            text: Text to convert
            output_path: Path to save audio
            speed: Speech speed
            
        Returns:
            bool: Success status
        """
        try:
            from gtts import gTTS
            import librosa
            
            # Create gTTS object for Urdu
            slow_mode = (speed < 0.8)  # Use slow mode if speed is below 0.8
            tts = gTTS(text=text, lang='ur', slow=slow_mode)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                temp_mp3 = tmp.name
            
            tts.save(temp_mp3)
            
            # Convert MP3 to WAV and adjust speed if needed
            if speed != 1.0:
                # Load and adjust speed
                y, sr = librosa.load(temp_mp3, sr=self.sample_rate)
                y_stretched = librosa.effects.time_stretch(y, rate=speed)
                sf.write(output_path, y_stretched, sr)
            else:
                # Just convert MP3 to WAV
                y, sr = librosa.load(temp_mp3, sr=self.sample_rate)
                sf.write(output_path, y, sr)
            
            # Clean up temporary file
            os.unlink(temp_mp3)
            
            return os.path.exists(output_path)
            
        except ImportError as e:
            print(f"Required library not installed: {str(e)}")
            return False
        except Exception as e:
            print(f"Error with gTTS: {str(e)}")
            return False
    
    def _generate_fallback(self, text, output_path):
        """
        Fallback: Generate a silent audio file with warning message
        
        Args:
            text: Text that would have been converted
            output_path: Path to save audio
            
        Returns:
            bool: Success status
        """
        try:
            # Create a simple beep sound as placeholder
            duration = len(text) * 0.1  # Rough estimate of speech duration
            duration = max(1.0, min(duration, 10.0))  # Clamp between 1-10 seconds
            
            # Generate a simple beep pattern
            t = np.linspace(0, duration, int(self.sample_rate * duration))
            beep_freq = 440  # A4 note
            audio = 0.5 * np.sin(2 * np.pi * beep_freq * t)
            
            # Add some silence at start and end
            silence = np.zeros(int(self.sample_rate * 0.1))
            audio = np.concatenate([silence, audio, silence])
            
            sf.write(output_path, audio, self.sample_rate)
            return os.path.exists(output_path)
            
        except Exception as e:
            print(f"Error generating fallback audio: {str(e)}")
            return False
    
    def adjust_audio_speed(self, audio_path, output_path, speed=1.0):
        """
        Adjust audio playback speed without changing pitch
        
        Args:
            audio_path: Input audio file
            output_path: Output audio file
            speed: Speed multiplier (1.0 = normal)
        """
        try:
            import librosa
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Change speed
            y_stretched = librosa.effects.time_stretch(y, rate=speed)
            
            # Save
            sf.write(output_path, y_stretched, sr)
            return True
            
        except Exception as e:
            print(f"Error adjusting speed: {str(e)}")
            return False
    
    def add_audio_effects(self, audio_path, output_path, effect_type="normalize"):
        """
        Add audio effects to voice-over
        
        Args:
            audio_path: Input audio file
            output_path: Output audio file
            effect_type: Type of effect (normalize, compress, enhance)
        """
        try:
            # Read audio
            data, sr = sf.read(audio_path)
            
            if effect_type == "normalize":
                # Normalize audio levels
                max_val = np.max(np.abs(data))
                if max_val > 0:
                    data = data / max_val * 0.95
            
            elif effect_type == "compress":
                # Dynamic range compression
                threshold = 0.1
                ratio = 4
                data = np.where(
                    np.abs(data) > threshold,
                    np.sign(data) * (threshold + (np.abs(data) - threshold) / ratio),
                    data
                )
            
            elif effect_type == "enhance":
                # Enhance clarity using bandpass filter
                # Butterworth bandpass filter (300-3000 Hz)
                nyquist = sr / 2
                low = 300 / nyquist
                high = 3000 / nyquist
                
                # Filter design
                sos = signal.butter(4, [low, high], 'band', output='sos')
                data = signal.sosfilt(sos, data)
                
                # Normalize after filtering
                max_val = np.max(np.abs(data))
                if max_val > 0:
                    data = data / max_val * 0.95
            
            # Save processed audio
            sf.write(output_path, data, sr)
            return True
            
        except Exception as e:
            print(f"Error adding effects: {str(e)}")
            return False
    
    def merge_audio_files(self, audio_files, output_path, crossfade=0.5):
        """
        Merge multiple audio files with optional crossfade
        
        Args:
            audio_files: List of audio file paths
            output_path: Path to save merged audio
            crossfade: Crossfade duration in seconds
        """
        try:
            combined_audio = np.array([])
            sr = None
            
            for i, audio_file in enumerate(audio_files):
                if not os.path.exists(audio_file):
                    print(f"Warning: Audio file not found: {audio_file}")
                    continue
                    
                data, current_sr = sf.read(audio_file)
                
                # Set sample rate from first file
                if sr is None:
                    sr = current_sr
                elif sr != current_sr:
                    # Resample if sample rates don't match
                    import librosa
                    data = librosa.resample(data, orig_sr=current_sr, target_sr=sr)
                
                if i == 0:
                    combined_audio = data
                else:
                    # Calculate crossfade samples
                    fade_samples = int(crossfade * sr)
                    
                    if fade_samples > 0 and len(combined_audio) > fade_samples:
                        # Create crossfade
                        fade_out = np.linspace(1, 0, min(fade_samples, len(combined_audio)))
                        fade_in = np.linspace(0, 1, min(fade_samples, len(data)))
                        
                        # Apply crossfade
                        combined_audio[-len(fade_out):] *= fade_out
                        data[:len(fade_in)] *= fade_in
                        
                        # Merge
                        min_length = min(len(fade_out), len(fade_in))
                        merged_part = combined_audio[-min_length:] + data[:min_length]
                        combined_audio = np.concatenate([
                            combined_audio[:-min_length],
                            merged_part,
                            data[min_length:]
                        ])
                    else:
                        combined_audio = np.concatenate([combined_audio, data])
            
            # Save merged audio
            if len(combined_audio) > 0 and sr is not None:
                sf.write(output_path, combined_audio, sr)
                return True
            return False
            
        except Exception as e:
            print(f"Error merging audio: {str(e)}")
            return False
    
    def validate_audio(self, audio_path):
        """
        Validate audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            (is_valid, duration_seconds)
        """
        try:
            if not os.path.exists(audio_path):
                return False, 0
            
            data, sr = sf.read(audio_path)
            duration = len(data) / sr
            return True, duration
            
        except Exception as e:
            print(f"Error validating audio: {str(e)}")
            return False, 0
    
    def get_audio_duration(self, audio_path):
        """Get audio duration in seconds"""
        try:
            if os.path.exists(audio_path):
                data, sr = sf.read(audio_path)
                return len(data) / sr
            return 0
        except:
            return 0
