import os
import tempfile
from pathlib import Path
import numpy as np
import logging
import subprocess
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try importing moviepy with different approaches
try:
    # Try new import style
    from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
    from moviepy.video.VideoClip import ColorClip
    logger.info("Imported MoviePy with new style")
except ImportError:
    try:
        # Try old import style
        from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, ColorClip
        logger.info("Imported MoviePy with old style")
    except ImportError as e:
        logger.error(f"Failed to import MoviePy: {e}")
        # Create dummy classes for testing
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

from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import cv2
from datetime import datetime

class VideoProcessor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"Temporary directory created: {self.temp_dir}")
        
    def generate_urdu_voice(self, text, output_path, lang='ur'):
        """Generate Urdu voice from text using gTTS"""
        try:
            # Clean text for better voice generation
            text = text.strip()
            if not text:
                logger.error("Empty text provided for voice generation")
                return False
                
            logger.info(f"Generating voice for text length: {len(text)}")
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(output_path)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"Voice generated successfully: {output_path}")
                return True
            else:
                logger.error("Voice file is empty or not created")
                return False
                
        except Exception as e:
            logger.error(f"Error generating voice: {e}")
            return False
    
    def combine_videos(self, video_paths, output_path, voice_path=None):
        """Combine multiple video clips into one video"""
        try:
            # Check if we have valid video paths
            if not video_paths:
                logger.error("No video paths provided")
                return False
            
            # Check if moviepy is available
            if VideoFileClip.__name__ == 'DummyClip':
                logger.error("MoviePy is not properly installed")
                return False
            
            clips = []
            target_width = 1280
            target_height = 720
            
            for i, video_path in enumerate(video_paths):
                try:
                    if not os.path.exists(video_path):
                        logger.error(f"Video file does not exist: {video_path}")
                        continue
                        
                    logger.info(f"Processing video {i+1}/{len(video_paths)}: {video_path}")
                    clip = VideoFileClip(video_path)
                    
                    # Skip if clip is invalid
                    if clip is None or clip.duration <= 0:
                        logger.error(f"Invalid clip: {video_path}")
                        continue
                    
                    # Resize clip to target height while maintaining aspect ratio
                    clip_resized = clip.resize(height=target_height)
                    
                    # Create a black background if needed
                    if clip_resized.w < target_width:
                        background = ColorClip(size=(target_width, target_height), color=(0,0,0))
                        background = background.set_duration(clip_resized.duration)
                        clip_resized = clip_resized.set_position(('center', 'center'))
                        clip_resized = CompositeVideoClip([background, clip_resized])
                    
                    clips.append(clip_resized)
                    
                except Exception as e:
                    logger.error(f"Error processing video {video_path}: {e}")
                    continue
            
            if not clips:
                logger.error("No valid video clips to process")
                return False
            
            # Concatenate all clips
            logger.info("Concatenating video clips...")
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Add voice if provided
            if voice_path and os.path.exists(voice_path) and os.path.getsize(voice_path) > 0:
                try:
                    logger.info("Adding voice overlay...")
                    voice_clip = AudioFileClip(voice_path)
                    # If voice is longer than video, trim it
                    if voice_clip.duration > final_video.duration:
                        voice_clip = voice_clip.subclip(0, final_video.duration)
                    final_video = final_video.set_audio(voice_clip)
                except Exception as e:
                    logger.error(f"Error adding voice: {e}")
            
            # Write final video
            logger.info(f"Writing final video to {output_path}")
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
            
            # Close all clips to free memory
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
                
            # Verify output file was created
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info("Video combination completed successfully")
                return True
            else:
                logger.error("Output video file is empty or not created")
                return False
            
        except Exception as e:
            logger.error(f"Error combining videos: {e}")
            return False
    
    def generate_thumbnail(self, video_path, output_path, text=None):
        """Generate thumbnail from video with optional text overlay"""
        try:
            if not os.path.exists(video_path):
                logger.error(f"Video file does not exist: {video_path}")
                return False
                
            # Capture frame from video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Could not open video file: {video_path}")
                return False
                
            # Try to get a frame from the middle of the video
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames > 0:
                frame_pos = total_frames // 3
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                logger.error("Could not capture frame from video")
                return False
                
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # Resize to standard thumbnail size
            pil_image.thumbnail((1280, 720), Image.Resampling.LANCZOS)
            
            # Add text overlay if provided
            if text:
                draw = ImageDraw.Draw(pil_image)
                
                # Try different font paths
                font = None
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                    "/System/Library/Fonts/Helvetica.ttc",
                    "/System/Library/Fonts/Arial.ttf",
                    "C:\\Windows\\Fonts\\arial.ttf",
                    "C:\\Windows\\Fonts\\segoeui.ttf"
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
                try:
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                except:
                    text_width = len(text) * 20
                    text_height = 40
                
                # Position text at bottom center
                x = (pil_image.width - text_width) // 2
                y = pil_image.height - text_height - 50
                
                # Draw background rectangle
                draw.rectangle(
                    [x-20, y-15, x+text_width+20, y+text_height+15],
                    fill=(0, 0, 0, 180)
                )
                
                # Draw text
                draw.text((x, y), text, fill=(255, 255, 255), font=font)
            
            # Save thumbnail
            pil_image.save(output_path, 'JPEG', quality=85)
            logger.info(f"Thumbnail generated: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            return False
    
    def get_video_duration(self, video_path):
        """Get duration of video file"""
        try:
            if not os.path.exists(video_path):
                return 0
                
            if VideoFileClip.__name__ != 'DummyClip':
                clip = VideoFileClip(video_path)
                duration = clip.duration
                clip.close()
                return duration
            else:
                # Fallback to OpenCV
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
        """Generate video description based on script and metadata"""
        try:
            # Calculate duration in minutes and seconds
            minutes = int(video_duration // 60)
            seconds = int(video_duration % 60)
            duration_str = f"{minutes}:{seconds:02d}"
            
            # Create a structured description
            description = f"""🎬 ویڈیو کی تفصیل:

{script_text[:500]}...

📊 ویڈیو کی معلومات:
• کل دورانیہ: {duration_str} منٹ
• کلپس کی تعداد: {clip_count}
• تاریخ تخلیق: {datetime.now().strftime('%Y-%m-%d')}
• معیار: HD (720p)

✨ خصوصیات:
• اعلیٰ معیار کی ویڈیو
• پیشہ ورانہ اردو آواز
• جدید ویڈیو ایڈیٹنگ

👍 اگر ویڈیو پسند آئے تو:
✅ لائک کریں
✅ سبسکرائب کریں
✅ شیئر کریں

#videoediting #urducontent #viral #trending #pakistan #india
"""
            return description
        except Exception as e:
            logger.error(f"Error generating description: {e}")
            return "ویڈیو کی تفصیل دستیاب نہیں ہے۔"
    
    def generate_title(self, script_text):
        """Generate video title from script content"""
        try:
            # Take first few words from script as title
            words = script_text.split()[:10]
            title = " ".join(words)
            if len(title) > 60:
                title = title[:57] + "..."
            
            # Add prefix if title is too short
            if len(title) < 10:
                title = f"نئی ویڈیو - {title}"
                
            return title
        except Exception as e:
            logger.error(f"Error generating title: {e}")
            return "نئی شاندار ویڈیو"
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")
