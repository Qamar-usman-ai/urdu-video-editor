import os
import tempfile
import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try importing moviepy with proper error handling
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
    from moviepy.video.VideoClip import ColorClip
    MOVIEPY_AVAILABLE = True
    logger.info("MoviePy imported successfully")
except ImportError as e:
    logger.error(f"MoviePy import failed: {e}")
    MOVIEPY_AVAILABLE = False
    # Create dummy class for fallback
    class DummyClip:
        def __init__(self, *args, **kwargs):
            pass
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    VideoFileClip = DummyClip
    AudioFileClip = DummyClip
    concatenate_videoclips = lambda *args, **kwargs: None
    CompositeVideoClip = DummyClip
    ColorClip = DummyClip

# Import other libraries
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.error("gTTS not installed")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.error("PIL not installed")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.error("OpenCV not installed")

from datetime import datetime

class VideoProcessor:
    def __init__(self):
        """Initialize the video processor with a temporary directory"""
        try:
            self.temp_dir = tempfile.mkdtemp()
            logger.info(f"Temporary directory created: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Failed to create temp directory: {e}")
            self.temp_dir = os.path.join(os.getcwd(), "temp_video_editor")
            os.makedirs(self.temp_dir, exist_ok=True)
            logger.info(f"Using fallback temp directory: {self.temp_dir}")
        
    def generate_urdu_voice(self, text, output_path, lang='ur'):
        """Generate Urdu voice from text using gTTS"""
        if not GTTS_AVAILABLE:
            logger.error("gTTS is not available. Please install it: pip install gTTS")
            return False
            
        try:
            # Clean and validate text
            text = text.strip()
            if not text:
                logger.error("Empty text provided for voice generation")
                return False
                
            logger.info(f"Generating voice for text length: {len(text)} characters")
            
            # Limit text length to avoid issues
            if len(text) > 5000:
                logger.warning(f"Text too long ({len(text)} chars), truncating to 5000")
                text = text[:5000]
            
            # Generate voice
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(output_path)
            
            # Verify file was created
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"Voice generated successfully: {output_path} ({os.path.getsize(output_path)} bytes)")
                return True
            else:
                logger.error("Voice file is empty or not created")
                return False
                
        except Exception as e:
            logger.error(f"Error generating voice: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def combine_videos(self, video_paths, output_path, voice_path=None):
        """Combine multiple video clips into one video"""
        if not MOVIEPY_AVAILABLE:
            logger.error("MoviePy is not available. Please install it: pip install moviepy")
            return False
            
        if not video_paths:
            logger.error("No video paths provided")
            return False
        
        try:
            # Filter valid video paths
            valid_paths = []
            for path in video_paths:
                if os.path.exists(path) and os.path.getsize(path) > 0:
                    valid_paths.append(path)
                else:
                    logger.warning(f"Skipping invalid video: {path}")
            
            if not valid_paths:
                logger.error("No valid video files to process")
                return False
            
            logger.info(f"Processing {len(valid_paths)} valid videos out of {len(video_paths)} total")
            
            clips = []
            target_width = 1280
            target_height = 720
            
            # Process each video
            for i, video_path in enumerate(valid_paths):
                try:
                    logger.info(f"Loading video {i+1}/{len(valid_paths)}: {os.path.basename(video_path)}")
                    clip = VideoFileClip(video_path)
                    
                    if clip is None or clip.duration <= 0:
                        logger.error(f"Invalid clip duration: {clip.duration if clip else 'None'}")
                        continue
                    
                    logger.info(f"Original clip: duration={clip.duration:.2f}s, size={clip.size}")
                    
                    # Resize to target height while maintaining aspect ratio
                    clip_resized = clip.resize(height=target_height)
                    
                    # Create composite with black background if needed
                    if abs(clip_resized.w - target_width) > 10:
                        logger.info(f"Adjusting clip from {clip_resized.w}x{clip_resized.h} to {target_width}x{target_height}")
                        background = ColorClip(size=(target_width, target_height), color=(0,0,0))
                        background = background.set_duration(clip_resized.duration)
                        clip_resized = clip_resized.set_position(('center', 'center'))
                        clip_resized = CompositeVideoClip([background, clip_resized])
                    
                    clips.append(clip_resized)
                    logger.info(f"Video {i+1} processed successfully")
                    
                except Exception as e:
                    logger.error(f"Error processing video {video_path}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            if not clips:
                logger.error("No clips were successfully loaded")
                return False
            
            # Concatenate all clips
            logger.info(f"Concatenating {len(clips)} clips...")
            try:
                final_video = concatenate_videoclips(clips, method="compose")
                logger.info(f"Concatenation successful. Final duration: {final_video.duration:.2f}s")
            except Exception as e:
                logger.error(f"Error during concatenation: {e}")
                return False
            
            # Add voice if provided
            if voice_path and os.path.exists(voice_path) and os.path.getsize(voice_path) > 0:
                try:
                    logger.info(f"Adding voice overlay from {voice_path}")
                    voice_clip = AudioFileClip(voice_path)
                    logger.info(f"Voice duration: {voice_clip.duration:.2f}s")
                    
                    # Trim voice if longer than video
                    if voice_clip.duration > final_video.duration:
                        logger.info(f"Trimming voice to match video duration")
                        voice_clip = voice_clip.subclip(0, final_video.duration)
                    
                    final_video = final_video.set_audio(voice_clip)
                    logger.info("Voice added successfully")
                except Exception as e:
                    logger.error(f"Error adding voice: {e}")
            
            # Write final video
            logger.info(f"Writing final video to {output_path}")
            try:
                final_video.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    fps=24,
                    preset='medium',
                    threads=2,
                    verbose=False,
                    logger=None
                )
                logger.info(f"Video written successfully")
            except Exception as e:
                logger.error(f"Error writing video: {e}")
                return False
            
            # Clean up clips
            for clip in clips:
                try:
                    clip.close()
                except:
                    pass
            try:
                final_video.close()
            except:
                pass
            if voice_path and 'voice_clip' in locals():
                try:
                    voice_clip.close()
                except:
                    pass
            
            # Verify output
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"Video combination complete. Output size: {os.path.getsize(output_path)} bytes")
                return True
            else:
                logger.error("Output file is empty or missing")
                return False
                
        except Exception as e:
            logger.error(f"Error combining videos: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_thumbnail(self, video_path, output_path, text=None):
        """Generate thumbnail from video with optional text overlay"""
        if not CV2_AVAILABLE:
            logger.error("OpenCV not available. Please install: pip install opencv-python")
            return False
            
        try:
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return False
                
            logger.info(f"Generating thumbnail from {video_path}")
            
            # Capture frame from video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Could not open video file: {video_path}")
                return False
            
            # Get a frame from the middle
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames > 0:
                frame_pos = min(total_frames // 3, total_frames - 1)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                logger.error("Could not capture frame from video")
                return False
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # Resize to thumbnail size
            pil_image.thumbnail((1280, 720), Image.Resampling.LANCZOS)
            
            # Add text overlay if provided
            if text:
                draw = ImageDraw.Draw(pil_image)
                
                # Try to find a font
                font = None
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                    "/System/Library/Fonts/Helvetica.ttc",
                    "C:\\Windows\\Fonts\\arial.ttf"
                ]
                
                for font_path in font_paths:
                    try:
                        font = ImageFont.truetype(font_path, 48)
                        break
                    except:
                        continue
                
                if font is None:
                    font = ImageFont.load_default()
                
                # Calculate text position
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (pil_image.width - text_width) // 2
                y = pil_image.height - text_height - 50
                
                # Draw background
                draw.rectangle(
                    [x-20, y-15, x+text_width+20, y+text_height+15],
                    fill=(0, 0, 0, 180)
                )
                
                # Draw text
                draw.text((x, y), text, fill=(255, 255, 255), font=font)
            
            # Save thumbnail
            pil_image.save(output_path, 'JPEG', quality=85)
            logger.info(f"Thumbnail saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_video_duration(self, video_path):
        """Get duration of video file"""
        try:
            if not os.path.exists(video_path):
                return 0
                
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            if fps > 0:
                return frame_count / fps
            return 0
        except:
            return 0
    
    def generate_description(self, script_text, video_duration, clip_count):
        """Generate video description"""
        try:
            minutes = int(video_duration // 60)
            seconds = int(video_duration % 60)
            duration_str = f"{minutes}:{seconds:02d}"
            
            description = f"""🎬 ویڈیو کی تفصیل:

{script_text[:500]}...

📊 ویڈیو کی معلومات:
• کل دورانیہ: {duration_str} منٹ
• کلپس کی تعداد: {clip_count}
• تاریخ تخلیق: {datetime.now().strftime('%Y-%m-%d')}

✨ خصوصیات:
• اعلیٰ معیار کی ویڈیو
• پیشہ ورانہ اردو آواز

👍 اگر ویڈیو پسند آئے تو لائک اور شیئر کریں!

#videoediting #urducontent #viral #trending
"""
            return description
        except Exception as e:
            logger.error(f"Error generating description: {e}")
            return "ویڈیو کی تفصیل دستیاب نہیں ہے۔"
    
    def generate_title(self, script_text):
        """Generate video title"""
        try:
            words = script_text.split()[:10]
            title = " ".join(words)
            if len(title) > 60:
                title = title[:57] + "..."
            return title if title else "نئی ویڈیو"
        except Exception as e:
            logger.error(f"Error generating title: {e}")
            return "نئی ویڈیو"
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

# Test the processor if run directly
if __name__ == "__main__":
    processor = VideoProcessor()
    print("VideoProcessor initialized successfully")
    print(f"MoviePy available: {MOVIEPY_AVAILABLE}")
    print(f"gTTS available: {GTTS_AVAILABLE}")
    print(f"PIL available: {PIL_AVAILABLE}")
    print(f"OpenCV available: {CV2_AVAILABLE}")
