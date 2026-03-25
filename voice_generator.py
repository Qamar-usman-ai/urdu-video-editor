import pyttsx3
import soundfile as sf
import numpy as np
from scipy import signal
import os

class VoiceGenerator:
    """Handles text-to-speech conversion with Urdu support"""
    
    def __init__(self):
        """Initialize text-to-speech engine"""
        self.engine = pyttsx3.init()
        self.sample_rate = 44100
    
    def generate_voice(self, text, output_path, speed=1.0, pitch=1.0):
        """
        Generate voice-over from Urdu text
        
        Args:
            text: Urdu text to convert to speech
            output_path: Path to save audio file
            speed: Speech speed (0.5-2.0, default 1.0)
            pitch: Pitch level (0.5-2.0, default 1.0)
            
        Returns:
            bool: Success status
        """
        try:
            # Configure engine
            self.engine.setProperty('rate', 150 * speed)  # Words per minute
            self.engine.setProperty('pitch', pitch)
            self.engine.setProperty('volume', 1.0)
            
            # Set voice to male (index 0 is usually male)
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id)
            
            # Save to temporary file first
            temp_file = output_path + ".tmp.wav"
            
            # Generate speech
            self.engine.save_to_file(text, temp_file)
            self.engine.runAndWait()
            
            # If temp file was created, convert/process it
            if os.path.exists(temp_file):
                os.rename(temp_file, output_path)
                return True
            else:
                # Fallback: use gTTS for Urdu
                return self._generate_with_gtts(text, output_path, speed)
            
        except Exception as e:
            print(f"Error generating voice: {str(e)}")
            return self._generate_with_gtts(text, output_path, speed)
    
    def _generate_with_gtts(self, text, output_path, speed=1.0):
        """
        Fallback: Generate voice using Google Text-to-Speech
        
        Args:
            text: Text to convert
            output_path: Path to save audio
            speed: Speech speed
            
        Returns:
            bool: Success status
        """
        try:
            from gtts import gTTS
            
            # Create gTTS object for Urdu
            tts = gTTS(text=text, lang='ur', slow=(speed < 1.0))
            tts.save(output_path)
            
            return True
            
        except ImportError:
            print("gTTS not available. Using pyttsx3 fallback...")
            return self._generate_with_pyttsx3(text, output_path, speed)
        except Exception as e:
            print(f"Error with gTTS: {str(e)}")
            return False
    
    def _generate_with_pyttsx3(self, text, output_path, speed=1.0):
        """
        Fallback: Basic pyttsx3 without file save
        
        Args:
            text: Text to convert
            output_path: Path to save audio
            speed: Speech speed
            
        Returns:
            bool: Success status
        """
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150 * speed)
            engine.setProperty('volume', 1.0)
            
            # Get available voices (male voice)
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)
            
            # Save to file
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            engine.stop()
            
            return os.path.exists(output_path)
            
        except Exception as e:
            print(f"Error with pyttsx3: {str(e)}")
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
                # Enhance clarity
                sos = signal.butter(4, [300, 3000], 'band', fs=sr, output='sos')
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
                data, sr = sf.read(audio_file)
                
                if i == 0:
                    combined_audio = data
                else:
                    # Calculate crossfade samples
                    fade_samples = int(crossfade * sr)
                    
                    if fade_samples > 0:
                        # Create crossfade
                        fade_out = np.linspace(1, 0, fade_samples)
                        fade_in = np.linspace(0, 1, fade_samples)
                        
                        # Apply crossfade
                        combined_audio[-fade_samples:] *= fade_out
                        data[:fade_samples] *= fade_in
                        
                        # Merge
                        combined_audio = np.concatenate([
                            combined_audio[:-fade_samples],
                            combined_audio[-fade_samples:] + data[:fade_samples],
                            data[fade_samples:]
                        ])
                    else:
                        combined_audio = np.concatenate([combined_audio, data])
            
            # Save merged audio
            sf.write(output_path, combined_audio, sr)
            return True
            
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
            data, sr = sf.read(audio_path)
            duration = len(data) / sr
            return True, duration
            
        except Exception as e:
            print(f"Error validating audio: {str(e)}")
            return False, 0
    
    def get_audio_duration(self, audio_path):
        """Get audio duration in seconds"""
        try:
            data, sr = sf.read(audio_path)
            return len(data) / sr
        except:
            return 0
