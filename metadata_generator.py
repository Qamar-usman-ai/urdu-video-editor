import json
from datetime import datetime
import hashlib
from typing import Dict, Any, Optional

class MetadataGenerator:
    """Generates metadata, titles, and descriptions for videos"""
    
    def __init__(self):
        """Initialize metadata generator"""
        self.categories = {
            "علوم و تعلیم": "Education",
            "تفریح": "Entertainment",
            "خبریں": "News",
            "ٹیکنالوجی": "Technology",
            "دوسرہ": "Other"
        }
    
    def generate_metadata(self, 
                         title: str,
                         description: str,
                         category: str,
                         video_duration: float,
                         script: str,
                         author: str = "Urdu Creator",
                         tags: Optional[list] = None) -> Dict[str, Any]:
        """
        Generate complete metadata for video
        
        Args:
            title: Video title
            description: Video description
            category: Video category
            video_duration: Duration in seconds
            script: Original script/text
            author: Creator name
            tags: List of tags
            
        Returns:
            Dictionary containing all metadata
        """
        
        # Generate video ID (hash of title + timestamp)
        video_id = self._generate_video_id(title)
        
        # Extract keywords from script
        keywords = self._extract_keywords(script)
        
        # Generate auto description if not provided
        if not description or description.strip() == "":
            description = self._generate_description(title, script)
        
        # Generate tags if not provided
        if not tags:
            tags = self._generate_tags(title, script, category)
        
        # Create metadata dictionary
        metadata = {
            "video_id": video_id,
            "title": title,
            "description": description,
            "category": category,
            "category_en": self.categories.get(category, category),
            "duration_seconds": video_duration,
            "duration_formatted": self._format_duration(video_duration),
            "author": author,
            "created_at": datetime.now().isoformat(),
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "created_time": datetime.now().strftime("%H:%M:%S"),
            "script": script,
            "keywords": keywords,
            "tags": tags,
            "language": "Urdu",
            "video_specs": {
                "format": "mp4",
                "codec_video": "h264",
                "codec_audio": "aac",
                "resolution": "1280x720",
                "fps": 30
            },
            "seo": {
                "meta_title": title,
                "meta_description": description[:160],
                "meta_keywords": ", ".join(tags[:5])
            },
            "statistics": {
                "estimated_views": 0,
                "estimated_watch_time": self._estimate_watch_time(video_duration),
                "engagement_rate": "0%"
            }
        }
        
        return metadata
    
    def generate_youtube_metadata(self, 
                                 title: str,
                                 description: str,
                                 tags: list,
                                 category: str = "22") -> Dict[str, str]:
        """
        Generate YouTube-specific metadata
        
        Args:
            title: Video title (max 100 chars)
            description: Video description (max 5000 chars)
            tags: List of tags
            category: YouTube category ID
            
        Returns:
            Dictionary with YouTube metadata
        """
        
        # Validate and trim
        title = title[:100]
        description = description[:5000]
        tags = tags[:30]  # Max 30 tags
        
        return {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category,
            "madeForKids": False,
            "license": "creativeCommon"
        }
    
    def _generate_video_id(self, title: str) -> str:
        """Generate unique video ID"""
        content = f"{title}{datetime.now().isoformat()}".encode()
        return hashlib.sha256(content).hexdigest()[:12]
    
    def _extract_keywords(self, text: str) -> list:
        """
        Extract keywords from script
        
        Args:
            text: Input text
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction
        words = text.split()
        # Filter short words and common Urdu stop words
        stop_words = {'اور', 'کے', 'ہے', 'یہ', 'میں', 'کو', 'ان', 'جو', 'سے', 'تو', 'بھی'}
        
        keywords = [
            word for word in words 
            if len(word) > 3 and word not in stop_words
        ][:10]
        
        return keywords
    
    def _generate_description(self, title: str, script: str) -> str:
        """
        Auto-generate video description
        
        Args:
            title: Video title
            script: Original script
            
        Returns:
            Generated description
        """
        # Get first 300 characters of script
        script_snippet = script[:300] if len(script) > 300 else script
        
        description = f"""{title}

{script_snippet}

---
✅ مکمل تفصیل اوپر دیے گئے اسکرپٹ میں موجود ہے۔

🎬 یہ ویڈیو اردو میں بنائی گئی ہے۔
🇵🇰 پاکستانی کریٹرز کے لیے خصوصی۔

براہ کرم سبسکرائب کریں! 📢
"""
        return description
    
    def _generate_tags(self, title: str, script: str, category: str) -> list:
        """
        Generate relevant tags
        
        Args:
            title: Video title
            script: Video script
            category: Video category
            
        Returns:
            List of relevant tags
        """
        tags = []
        
        # Add title words as tags
        title_words = title.split()[:3]
        tags.extend(title_words)
        
        # Add category
        tags.append(category)
        
        # Add relevant Urdu tags
        urdu_tags = [
            "اردو ویڈیو",
            "پاکستانی",
            "اردو کہانی",
            "Urdu Video",
            "Pakistani"
        ]
        tags.extend(urdu_tags[:3])
        
        # Add keywords from script
        keywords = self._extract_keywords(script)
        tags.extend(keywords[:5])
        
        # Remove duplicates and return
        return list(set(tags))[:20]
    
    def _format_duration(self, seconds: float) -> str:
        """
        Format duration as HH:MM:SS
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def _estimate_watch_time(self, duration: float) -> str:
        """
        Estimate average watch time
        
        Args:
            duration: Video duration in seconds
            
        Returns:
            Estimated watch time string
        """
        # Assume 80% average retention
        watch_time = duration * 0.8
        return self._format_duration(watch_time)
    
    def export_metadata_json(self, metadata: dict, file_path: str) -> bool:
        """
        Export metadata to JSON file
        
        Args:
            metadata: Metadata dictionary
            file_path: Output file path
            
        Returns:
            Success status
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting metadata: {str(e)}")
            return False
    
    def export_for_youtube(self, metadata: dict, file_path: str) -> bool:
        """
        Export metadata in YouTube-compatible format
        
        Args:
            metadata: Metadata dictionary
            file_path: Output file path
            
        Returns:
            Success status
        """
        try:
            youtube_meta = self.generate_youtube_metadata(
                title=metadata.get('title', ''),
                description=metadata.get('description', ''),
                tags=metadata.get('tags', []),
                category='26'  # Howto & Style category
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(youtube_meta, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting YouTube metadata: {str(e)}")
            return False
    
    def generate_thumbnail_text(self, metadata: dict) -> Dict[str, str]:
        """
        Generate text to overlay on thumbnail
        
        Args:
            metadata: Video metadata
            
        Returns:
            Dictionary with text and styling
        """
        title = metadata.get('title', '')
        category = metadata.get('category', '')
        
        # Truncate title for thumbnail
        title_short = title[:25] + "..." if len(title) > 25 else title
        
        return {
            "main_text": title_short,
            "sub_text": category,
            "text_color": "white",
            "background_color": "black",
            "position": "center",
            "font_size": "large"
        }
    
    def create_srt_subtitle(self, script: str, duration: float, output_path: str) -> bool:
        """
        Create SRT subtitle file from script
        
        Args:
            script: Full script text
            duration: Video duration in seconds
            output_path: Path to save SRT file
            
        Returns:
            Success status
        """
        try:
            # Split script into chunks
            sentences = script.split('۔')  # Urdu period
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return False
            
            # Calculate time per sentence
            time_per_sentence = duration / len(sentences)
            
            srt_content = ""
            for i, sentence in enumerate(sentences):
                start_time = self._seconds_to_timecode(i * time_per_sentence)
                end_time = self._seconds_to_timecode((i + 1) * time_per_sentence)
                
                srt_content += f"{i + 1}\n"
                srt_content += f"{start_time} --> {end_time}\n"
                srt_content += f"{sentence}\n\n"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            return True
        except Exception as e:
            print(f"Error creating subtitles: {str(e)}")
            return False
    
    def _seconds_to_timecode(self, seconds: float) -> str:
        """
        Convert seconds to SRT timecode format (HH:MM:SS,mmm)
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Timecode string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
