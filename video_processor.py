import cv2
import os
import subprocess
import numpy as np
from pathlib import Path
import tempfile

class VideoProcessor:
    """Handles video combining, audio sync, and thumbnail generation"""
    
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.flv']
    
    def combine_videos(self, video_paths, output_path, quality="720p"):
        """
        Combine multiple video clips into one continuous video
        
        Args:
            video_paths: List of paths to video files
            output_path: Path to save combined video
            quality: Output quality (360p, 480p, 720p, 1080p)
        """
        try:
            # Get video properties from first clip
            cap = cv2.VideoCapture(video_paths[0])
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            
            # Adjust resolution based on quality
            quality_map = {
                "360p": (640, 360),
                "480p": (854, 480),
                "720p": (1280, 720),
                "1080p": (1920, 1080)
            }
            
            target_size = quality_map.get(quality, (1280, 720))
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, target_size)
            
            # Process each video file
            for video_path in video_paths:
                cap = cv2.VideoCapture(video_path)
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Resize frame to target size
                    resized_frame = cv2.resize(frame, target_size)
                    out.write(resized_frame)
                
                cap.release()
            
            out.release()
            return True
            
        except Exception as e:
            print(f"Error combining videos: {str(e)}")
            return False
    
    def add_audio_to_video(self, video_path, audio_path, output_path):
        """
        Add audio track to video using ffmpeg
        
        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            output_path: Path to save final video
        """
        try:
            command = [
                'ffmpeg',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-shortest',
                '-y',
                output_path
            ]
            
            subprocess.run(command, capture_output=True, check=True)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr.decode()}")
            return False
        except Exception as e:
            print(f"Error adding audio: {str(e)}")
            return False
    
    def generate_thumbnail(self, video_path, output_path, frame_index=1):
        """
        Generate thumbnail from video at specific frame
        
        Args:
            video_path: Path to video file
            output_path: Path to save thumbnail
            frame_index: Which second to capture (1 = 1 second in)
        """
        try:
            cap = cv2.VideoCapture(video_path)
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            # Jump to frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, fps * frame_index)
            
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Resize to YouTube thumbnail size (1280x720)
                frame = cv2.resize(frame, (1280, 720))
                
                # Add text overlay
                cv2.putText(
                    frame,
                    "Video Thumbnail",
                    (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2,
                    (255, 255, 255),
                    3
                )
                
                # Save as JPEG
                cv2.imwrite(output_path, frame)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error generating thumbnail: {str(e)}")
            return False
    
    def get_video_duration(self, video_path):
        """
        Get video duration in seconds
        
        Args:
            video_path: Path to video file
            
        Returns:
            Duration in seconds (float)
        """
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()
            
            duration = frame_count / fps
            return round(duration, 2)
            
        except Exception as e:
            print(f"Error getting duration: {str(e)}")
            return 0
    
    def resize_video(self, video_path, output_path, width, height):
        """
        Resize video to specific dimensions
        
        Args:
            video_path: Input video path
            output_path: Output video path
            width: Target width
            height: Target height
        """
        try:
            cap = cv2.VideoCapture(video_path)
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                resized = cv2.resize(frame, (width, height))
                out.write(resized)
            
            cap.release()
            out.release()
            return True
            
        except Exception as e:
            print(f"Error resizing video: {str(e)}")
            return False
    
    def validate_video(self, video_path):
        """
        Validate if video file is readable
        
        Args:
            video_path: Path to video file
            
        Returns:
            (is_valid, duration_seconds)
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return False, 0
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            
            cap.release()
            
            duration = frame_count / fps if fps > 0 else 0
            
            # Check if at least 5 seconds
            if duration >= 5:
                return True, duration
            
            return False, duration
            
        except Exception as e:
            print(f"Error validating video: {str(e)}")
            return False, 0
