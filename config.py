# Configuration file for Urdu Video Editor Pro

import os
from typing import Dict, Tuple

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

APP_NAME = "Urdu Video Editor Pro"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Pakistani Creators"

# ============================================================================
# VIDEO SETTINGS
# ============================================================================

# Supported video formats
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wav']

# Video quality settings
VIDEO_QUALITY_SETTINGS = {
    "360p": {
        "resolution": (640, 360),
        "bitrate": "800k",
        "description": "Mobile Optimized"
    },
    "480p": {
        "resolution": (854, 480),
        "bitrate": "1500k",
        "description": "Standard Quality"
    },
    "720p": {
        "resolution": (1280, 720),
        "bitrate": "2500k",
        "description": "HD Quality"
    },
    "1080p": {
        "resolution": (1920, 1080),
        "bitrate": "5000k",
        "description": "Full HD Quality"
    }
}

# Video codec settings
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "aac"
VIDEO_FPS = 30
VIDEO_CRF = 23  # Quality (0-51, lower = better)

# Minimum video requirements
MIN_VIDEO_DURATION = 5  # seconds
MIN_VIDEO_CLIPS = 5
MAX_SINGLE_VIDEO_SIZE = 500  # MB
MAX_TOTAL_SIZE = 2000  # MB

# ============================================================================
# AUDIO SETTINGS
# ============================================================================

# Audio sampling rate
AUDIO_SAMPLE_RATE = 44100

# Voice settings
VOICE_SETTINGS = {
    "default_speed": 1.0,
    "min_speed": 0.5,
    "max_speed": 2.0,
    "default_pitch": 1.0,
    "min_pitch": 0.5,
    "max_pitch": 2.0,
    "volume": 1.0
}

# Voice engine preferences (order matters)
VOICE_ENGINES = [
    "pyttsx3",      # Local, offline
    "gtts",         # Google TTS, online, better quality
    "fallback"      # Fallback option
]

# ============================================================================
# LANGUAGE & URDU SETTINGS
# ============================================================================

# Supported languages
SUPPORTED_LANGUAGES = {
    "urdu": "اردو",
    "english": "English",
    "roman_urdu": "Roman Urdu"
}

# Urdu-specific settings
URDU_SETTINGS = {
    "voice_gender": "male",  # male or female
    "accent": "pakistan",    # pakistan, india, etc.
    "script_type": "nastaliq"  # nastaliq, naskh, etc.
}

# Common Urdu stop words (for keyword extraction)
URDU_STOP_WORDS = {
    'اور', 'کے', 'ہے', 'یہ', 'میں', 'کو', 'ان', 'جو', 'سے', 'تو', 
    'بھی', 'ہیں', 'ہو', 'تھا', 'ہوں', 'ہیں', 'ہو', 'ہے', 'ہیں'
}

# ============================================================================
# CATEGORY SETTINGS
# ============================================================================

VIDEO_CATEGORIES = {
    "علوم و تعلیم": "Education",
    "تفریح": "Entertainment",
    "خبریں": "News",
    "ٹیکنالوجی": "Technology",
    "دوسرہ": "Other",
    "ورزش": "Sports",
    "سفر": "Travel",
    "کھانا": "Food",
    "موسیقی": "Music",
    "فن": "Arts"
}

# ============================================================================
# METADATA SETTINGS
# ============================================================================

# Default metadata values
DEFAULT_METADATA = {
    "author": "Urdu Creator",
    "language": "Urdu",
    "format": "mp4",
    "codec_video": "h264",
    "codec_audio": "aac"
}

# YouTube category IDs
YOUTUBE_CATEGORIES = {
    "Education": "27",
    "Entertainment": "24",
    "News": "25",
    "Technology": "28",
    "Sports": "17",
    "Travel": "19",
    "Food": "26",
    "Music": "10",
    "Arts": "29"
}

# Thumbnail settings
THUMBNAIL_SETTINGS = {
    "resolution": (1280, 720),
    "format": "jpg",
    "quality": 95,
    "frame_offset": 1  # seconds into video
}

# ============================================================================
# FILE & DIRECTORY SETTINGS
# ============================================================================

# Temporary directory
TEMP_DIR = os.path.join(os.path.expanduser("~"), ".urdu-video-editor", "temp")
OUTPUT_DIR = os.path.join(os.path.expanduser("~"), ".urdu-video-editor", "output")

# Create directories if they don't exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# File naming
FILE_NAMING_CONVENTION = {
    "combined_video": "combined_{timestamp}.mp4",
    "voiceover_audio": "voiceover_{timestamp}.wav",
    "final_video": "final_video_{timestamp}.mp4",
    "thumbnail": "thumbnail_{timestamp}.jpg",
    "metadata": "metadata_{timestamp}.json",
    "subtitle": "subtitle_{timestamp}.srt"
}

# ============================================================================
# PROCESSING SETTINGS
# ============================================================================

# FFmpeg settings
FFMPEG_SETTINGS = {
    "preset": "medium",  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
    "threads": -1,  # -1 = auto detect
    "timeout": 3600  # seconds
}

# Processing timeouts
PROCESSING_TIMEOUTS = {
    "video_combine": 300,  # 5 minutes
    "voice_generation": 180,  # 3 minutes
    "audio_sync": 300,  # 5 minutes
    "thumbnail_gen": 30,  # 30 seconds
    "metadata_gen": 10  # 10 seconds
}

# ============================================================================
# UI & STREAMLIT SETTINGS
# ============================================================================

# Page configuration
STREAMLIT_CONFIG = {
    "page_title": "Urdu Video Editor Pro",
    "page_icon": "🎬",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Color scheme
COLOR_SCHEME = {
    "primary": "#FF6B6B",
    "secondary": "#4ECDC4",
    "success": "#95E1D3",
    "error": "#F38181",
    "warning": "#FECA57",
    "info": "#48DBFB"
}

# ============================================================================
# VALIDATION RULES
# ============================================================================

VALIDATION_RULES = {
    "title": {
        "min_length": 5,
        "max_length": 100,
        "required": True
    },
    "description": {
        "min_length": 10,
        "max_length": 5000,
        "required": False
    },
    "script": {
        "min_length": 10,
        "max_length": 10000,
        "required": True
    },
    "video_clips": {
        "min_count": 5,
        "max_count": 50,
        "min_duration": 5,  # seconds
        "max_duration": 600  # 10 minutes
    }
}

# ============================================================================
# ERROR MESSAGES
# ============================================================================

ERROR_MESSAGES = {
    "no_videos": "❌ لطفاً کم از کم ایک ویڈیو اپ لوڈ کریں",
    "insufficient_videos": "❌ لطفاً 5 یا زیادہ ویڈیو کلپس اپ لوڈ کریں",
    "no_script": "❌ براہ کرم اپنی اسکرپٹ درج کریں",
    "no_title": "❌ براہ کرم ویڈیو کا عنوان درج کریں",
    "invalid_video": "❌ غلط ویڈیو فارمیٹ",
    "video_too_short": "❌ ویڈیو کم از کم 5 سیکنڈ کی ہونی چاہیے",
    "processing_error": "❌ پروسیسنگ میں خرابی",
    "ffmpeg_not_found": "❌ FFmpeg انسٹال نہیں ہے"
}

# ============================================================================
# SUCCESS MESSAGES
# ============================================================================

SUCCESS_MESSAGES = {
    "videos_uploaded": "✅ {count} ویڈیو اپ لوڈ ہو گئی",
    "processing_complete": "✅ پروسیسنگ مکمل ہوئی!",
    "file_downloaded": "✅ فائل ڈاؤن لوڈ ہوئی",
    "voice_generated": "✅ صوت تیار ہو گئی"
}

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "file": os.path.join(TEMP_DIR, "app.log")
}

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================

PERFORMANCE_SETTINGS = {
    "max_workers": 4,  # For parallel processing
    "chunk_size": 1024 * 1024,  # 1MB chunks
    "buffer_size": 4096,
    "cache_enabled": True,
    "cache_expiry": 3600  # seconds
}

# ============================================================================
# FEATURE FLAGS
# ============================================================================

FEATURES = {
    "background_music": True,
    "subtitles": True,
    "transitions": False,  # Coming soon
    "effects": False,  # Coming soon
    "watermark": False,  # Coming soon
    "subtitle_sync": True,
    "multi_language": False,  # Coming soon
    "advanced_editing": False  # Coming soon
}

# ============================================================================
# DEFAULT CONFIGURATION
# ============================================================================

DEFAULT_CONFIG = {
    "quality": "720p",
    "voice_speed": 1.0,
    "voice_pitch": 1.0,
    "background_music": False,
    "category": "دوسرہ",
    "author": "اردو کریٹر",
    "language": "urdu"
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_video_quality_resolution(quality: str) -> Tuple[int, int]:
    """Get resolution tuple for quality setting"""
    return VIDEO_QUALITY_SETTINGS.get(quality, VIDEO_QUALITY_SETTINGS["720p"])["resolution"]

def get_category_english(urdu_category: str) -> str:
    """Convert Urdu category to English"""
    return VIDEO_CATEGORIES.get(urdu_category, "Other")

def get_youtube_category_id(english_category: str) -> str:
    """Get YouTube category ID"""
    return YOUTUBE_CATEGORIES.get(english_category, "29")

def is_valid_quality(quality: str) -> bool:
    """Validate quality setting"""
    return quality in VIDEO_QUALITY_SETTINGS

def is_supported_format(filename: str) -> bool:
    """Check if file format is supported"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in SUPPORTED_VIDEO_FORMATS
