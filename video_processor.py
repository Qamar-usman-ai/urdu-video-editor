import os
import tempfile
import logging
from pathlib import Path
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import required libraries
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
    MOVIEPY_OK = True
except ImportError:
    MOVIEPY_OK = False
    logger.error("MoviePy not installed. Run: pip install moviepy")

try:
    from gtts import gTTS
    GTTS_OK = True
except ImportError:
    GTTS_OK = False
    logger.error("gTTS not installed. Run: pip install gtts")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_OK = True
except ImportError:
    PIL_OK = False
    logger.error("PIL not installed. Run: pip install Pillow")

try:
    import cv2
    CV2_OK = True
except ImportError:
    CV2_OK = False
    logger.error("OpenCV not installed. Run: pip install opencv-python")

from datetime import datetime

class VideoProcessor:
    def __init__(self):
        """Initialize processor with temp directory"""
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"Temp dir created: {self.temp_dir}")
        
    def generate_urdu_voice(self, text, output_path):
        """Generate Urdu voice using gTTS"""
        if not GTTS_OK:
            logger.error("gTTS not available")
            return False
            
        try:
            text = text.strip()
            if not text:
                return False
                
            # Limit text length
            if len(text) > 3000:
                text = text[:3000]
                
            logger.info(f"Generating voice for {len(text)} chars")
            tts = gTTS(text=text, lang='ur', slow=False)
            tts.save(output_path)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"Voice saved: {output_path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Voice error: {e}")
            return False
    
    def combine_videos(self, video_paths, output_path, voice_path=None):
        """Combine videos using MoviePy"""
        if not MOVIEPY_OK:
            logger.error("MoviePy not available")
            return False
            
        if not video_paths:
            logger.error("No videos provided")
            return False
            
        try:
            # Filter valid videos
            valid_videos = []
            for vp in video_paths:
                if os.path.exists(vp) and os.path.getsize(vp) > 0:
                    valid_videos.append(vp)
                    logger.info(f"Valid video: {vp} ({os.path.getsize(vp)} bytes)")
                else:
                    logger.warning(f"Invalid video: {vp}")
            
            if not valid_videos:
                logger.error("No valid videos found")
                return False
            
            # Load and process each video
            clips = []
            target_height = 720
            
            for i, video_path in enumerate(valid_videos):
                try:
                    logger.info(f"Loading video {i+1}: {video_path}")
                    clip = VideoFileClip(video_path)
                    
                    if clip.duration <= 0:
                        logger.warning(f"Zero duration video: {video_path}")
                        continue
                    
                    # Resize to target height
                    clip = clip.resize(height=target_height)
                    clips.append(clip)
                    logger.info(f"Video {i+1} loaded, duration: {clip.duration:.2f}s")
                    
                except Exception as e:
                    logger.error(f"Error loading video {video_path}: {e}")
                    continue
            
            if not clips:
                logger.error("No clips could be loaded")
                return False
            
            # Concatenate videos
            logger.info(f"Concatenating {len(clips)} videos...")
            final_clip = concatenate_videoclips(clips, method="compose")
            logger.info(f"Final video duration: {final_clip.duration:.2f}s")
            
            # Add voice if available
            if voice_path and os.path.exists(voice_path):
                try:
                    logger.info("Adding voice overlay")
                    audio_clip = AudioFileClip(voice_path)
                    
                    # If audio longer than video, trim it
                    if audio_clip.duration > final_clip.duration:
                        audio_clip = audio_clip.subclip(0, final_clip.duration)
                    
                    final_clip = final_clip.set_audio(audio_clip)
                    logger.info("Voice added successfully")
                except Exception as e:
                    logger.error(f"Error adding voice: {e}")
            
            # Write final video
            logger.info(f"Writing video to {output_path}")
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=24,
                preset='ultrafast',  # Faster encoding
                threads=2,
                verbose=False,
                logger=None
            )
            
            # Clean up
            for clip in clips:
                clip.close()
            final_clip.close()
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"Video created successfully: {output_path}")
                return True
            else:
                logger.error("Output file not created")
                return False
                
        except Exception as e:
            logger.error(f"Error combining videos: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_thumbnail(self, video_path, output_path, text=None):
        """Generate thumbnail from video"""
        if not CV2_OK:
            logger.error("OpenCV not available")
            return False
            
        try:
            if not os.path.exists(video_path):
                logger.error(f"Video not found: {video_path}")
                return False
                
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error("Cannot open video")
                return False
            
            # Get frame from middle
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames > 0:
                frame_pos = total_frames // 2
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                logger.error("Cannot read frame")
                return False
            
            # Convert to PIL
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            # Resize
            img.thumbnail((1280, 720))
            
            # Add text if provided
            if text:
                draw = ImageDraw.Draw(img)
                
                # Try to get a font
                font = None
                try:
                    font = ImageFont.truetype("arial.ttf", 40)
                except:
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
                    except:
                        font = ImageFont.load_default()
                
                # Get text size
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Position at bottom
                x = (img.width - text_width) // 2
                y = img.height - text_height - 50
                
                # Draw background
                draw.rectangle([x-10, y-5, x+text_width+10, y+text_height+5], fill=(0,0,0,180))
                
                # Draw text
                draw.text((x, y), text, fill=(255,255,255), font=font)
            
            # Save
            img.save(output_path, 'JPEG', quality=85)
            logger.info(f"Thumbnail saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Thumbnail error: {e}")
            return False
    
    def get_video_duration(self, video_path):
        """Get video duration in seconds"""
        try:
            if not CV2_OK or not os.path.exists(video_path):
                return 0
                
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            if fps > 0:
                return frames / fps
            return 0
        except:
            return 0
    
    def generate_title(self, script_text):
        """Generate title from script"""
        try:
            words = script_text.split()[:8]
            title = " ".join(words)
            return title if title else "ویڈیو"
        except:
            return "ویڈیو"
    
    def generate_description(self, script_text, duration, clip_count):
        """Generate video description"""
        try:
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            
            desc = f"""🎬 ویڈیو کی تفصیل:

{script_text[:300]}...

📊 معلومات:
• دورانیہ: {minutes}:{seconds:02d}
• کلپس: {clip_count}
• تاریخ: {datetime.now().strftime('%Y-%m-%d')}

👍 لائک کریں اور سبسکرائب کریں!

#urduvideo #story #motivation
"""
            return desc
        except:
            return "ویڈیو کی تفصیل"
    
    def cleanup(self):
        """Clean up temp files"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up: {self.temp_dir}")
        except:
            pass
