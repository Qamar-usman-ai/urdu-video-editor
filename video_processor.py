import os
import tempfile
import subprocess
from pathlib import Path
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.fx import resize, crop
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import cv2
import hashlib
from datetime import datetime
import json

class VideoProcessor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def generate_urdu_voice(self, text, output_path, lang='ur'):
        """Generate Urdu voice from text using gTTS"""
        try:
            # gTTS supports Urdu with 'ur' language code
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(output_path)
            return True
        except Exception as e:
            print(f"Error generating voice: {e}")
            return False
    
    def combine_videos(self, video_paths, output_path, voice_path=None):
        """Combine multiple video clips into one video"""
        try:
            clips = []
            target_width = 1920
            target_height = 1080
            
            for video_path in video_paths:
                clip = VideoFileClip(video_path)
                
                # Resize clip to target resolution while maintaining aspect ratio
                clip_resized = clip.resize(height=target_height)
                if clip_resized.w < target_width:
                    # Add black borders if needed
                    clip_resized = clip_resized.resize(width=target_width)
                
                # Crop if needed
                if clip_resized.h > target_height:
                    clip_resized = clip_resized.crop(y_center=clip_resized.h/2, height=target_height)
                
                clips.append(clip_resized)
            
            # Concatenate all clips
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Add voice if provided
            if voice_path and os.path.exists(voice_path):
                voice_clip = AudioFileClip(voice_path)
                final_video = final_video.set_audio(voice_clip)
            
            # Write final video
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium',
                threads=4
            )
            
            # Close all clips
            for clip in clips:
                clip.close()
            final_video.close()
            if voice_path:
                voice_clip.close()
                
            return True
        except Exception as e:
            print(f"Error combining videos: {e}")
            return False
    
    def generate_thumbnail(self, video_path, output_path, text=None):
        """Generate thumbnail from video with optional text overlay"""
        try:
            # Capture frame from video
            cap = cv2.VideoCapture(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            # Get frame at 1/3 of video
            frame_pos = frame_count // 3
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # Add text overlay if provided
                if text:
                    draw = ImageDraw.Draw(pil_image)
                    
                    # Try to use a default font
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
                    except:
                        font = ImageFont.load_default()
                    
                    # Add semi-transparent background for text
                    text_bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    
                    # Position text at bottom center
                    x = (pil_image.width - text_width) // 2
                    y = pil_image.height - text_height - 50
                    
                    # Draw background rectangle
                    draw.rectangle(
                        [x-20, y-10, x+text_width+20, y+text_height+10],
                        fill=(0, 0, 0, 128)
                    )
                    
                    # Draw text
                    draw.text((x, y), text, fill=(255, 255, 255), font=font)
                
                # Save thumbnail
                pil_image.save(output_path, 'JPEG', quality=85)
                return True
            
            return False
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return False
    
    def generate_description(self, script_text, video_duration, clip_count):
        """Generate video description based on script and metadata"""
        try:
            # Create a structured description
            description = f"""🎬 ویڈیو کی تفصیل:

{script_text[:500]}...

📊 ویڈیو کی معلومات:
• کل دورانیہ: {video_duration:.2f} سیکنڈ
• کلپس کی تعداد: {clip_count}
• تاریخ تخلیق: {datetime.now().strftime('%Y-%m-%d')}

✨ خصوصیات:
• اعلیٰ معیار کی ویڈیو
• اردو آواز
• پیشہ ورانہ تدوین

👍 اگر ویڈیو پسند آئے تو لائک اور سبسکرائب کریں!

#video #urdu #content #viral #trending
"""
            return description
        except Exception as e:
            print(f"Error generating description: {e}")
            return "ویڈیو کی تفصیل دستیاب نہیں ہے۔"
    
    def generate_title(self, script_text):
        """Generate video title from script content"""
        try:
            # Take first few words from script as title
            words = script_text.split()[:7]
            title = " ".join(words)
            if len(title) > 60:
                title = title[:57] + "..."
            return title
        except Exception as e:
            print(f"Error generating title: {e}")
            return "نئی ویڈیو"
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except:
            pass
