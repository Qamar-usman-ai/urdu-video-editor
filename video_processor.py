import os
import tempfile
import subprocess
from pathlib import Path
import numpy as np

# Fix MoviePy imports with proper error handling
try:
    from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
except ImportError:
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips

from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import cv2
import hashlib
from datetime import datetime
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"Temporary directory created: {self.temp_dir}")
        
    def generate_urdu_voice(self, text, output_path, lang='ur'):
        """Generate Urdu voice from text using gTTS"""
        try:
            # gTTS supports Urdu with 'ur' language code
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(output_path)
            logger.info(f"Voice generated successfully: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error generating voice: {e}")
            return False
    
    def combine_videos(self, video_paths, output_path, voice_path=None):
        """Combine multiple video clips into one video"""
        try:
            clips = []
            target_width = 1280  # HD resolution
            target_height = 720
            
            for i, video_path in enumerate(video_paths):
                try:
                    logger.info(f"Processing video {i+1}/{len(video_paths)}: {video_path}")
                    clip = VideoFileClip(video_path)
                    
                    # Resize clip to target resolution while maintaining aspect ratio
                    clip_resized = clip.resize(height=target_height)
                    
                    # If width is less than target, add black borders
                    if clip_resized.w < target_width:
                        from moviepy.video.fx import crop
                        # Create black background
                        from moviepy.video.VideoClip import ColorClip
                        background = ColorClip(size=(target_width, target_height), color=(0,0,0))
                        background = background.set_duration(clip_resized.duration)
                        # Center the video
                        clip_resized = clip_resized.set_position(('center', 'center'))
                        clip_resized = CompositeVideoClip([background, clip_resized])
                    elif clip_resized.w > target_width:
                        # Crop if too wide
                        clip_resized = clip_resized.crop(x_center=clip_resized.w/2, width=target_width)
                    
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
            if voice_path and os.path.exists(voice_path):
                try:
                    logger.info("Adding voice overlay...")
                    voice_clip = AudioFileClip(voice_path)
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
                threads=4,
                verbose=False,
                logger=None
            )
            
            # Close all clips to free memory
            for clip in clips:
                clip.close()
            final_video.close()
            if voice_path and 'voice_clip' in locals():
                voice_clip.close()
                
            logger.info("Video combination completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error combining videos: {e}")
            return False
    
    def generate_thumbnail(self, video_path, output_path, text=None):
        """Generate thumbnail from video with optional text overlay"""
        try:
            # Capture frame from video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Could not open video file: {video_path}")
                return False
                
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            # Get frame at 1/3 of video, or first frame if video is short
            frame_pos = min(frame_count // 3, frame_count - 1) if frame_count > 3 else 0
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            ret, frame = cap.read()
            cap.release()
            
            if ret and frame is not None:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # Resize to standard thumbnail size
                pil_image.thumbnail((1280, 720), Image.Resampling.LANCZOS)
                
                # Add text overlay if provided
                if text:
                    draw = ImageDraw.Draw(pil_image)
                    
                    # Try different font paths
                    font_paths = [
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                        "/System/Library/Fonts/Helvetica.ttc",  # macOS
                        "C:\\Windows\\Fonts\\arial.ttf"  # Windows
                    ]
                    
                    font = None
                    for font_path in font_paths:
                        try:
                            font = ImageFont.truetype(font_path, 40)
                            break
                        except:
                            continue
                    
                    if font is None:
                        font = ImageFont.load_default()
                    
                    # Calculate text position
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
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
            
            logger.error("Could not capture frame from video")
            return False
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            return False
    
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
    
    def get_video_duration(self, video_path):
        """Get duration of video file"""
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration
            clip.close()
            return duration
        except:
            return 0
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")
