# 🎬 Urdu Video Editor Pro

A complete **Python + Streamlit** application for creating professional videos with Urdu voice-over. Combines multiple video clips, adds male voice narration in Urdu, generates thumbnails, and creates video metadata automatically.

## 🎯 Features

✅ **Multi-Clip Video Combining** - Merge 5+ video clips seamlessly  
✅ **Urdu Voice-Over** - Male voice text-to-speech in Urdu  
✅ **Auto Audio Sync** - Synchronize voice-over with video  
✅ **Thumbnail Generation** - Create YouTube-ready thumbnails  
✅ **Metadata Generation** - Auto-create titles, descriptions, tags  
✅ **Quality Options** - 360p, 480p, 720p, 1080p support  
✅ **SEO Optimized** - YouTube and platform-ready metadata  
✅ **Beautiful UI** - Responsive Streamlit interface  

## 📋 Requirements

### System Requirements
- **OS**: Windows, macOS, Linux
- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB (8GB+ recommended)
- **Storage**: 5GB free space for processing
- **FFmpeg**: Required for video processing

### Python Packages
All listed in `requirements.txt`

## 🚀 Installation

### Step 1: Install System Dependencies

**On Windows:**
```bash
# Install FFmpeg using Chocolatey
choco install ffmpeg
```

**On macOS:**
```bash
# Install FFmpeg using Homebrew
brew install ffmpeg
```

**On Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg python3-dev
```

### Step 2: Clone or Download Project

```bash
# Create a new directory
mkdir urdu-video-editor
cd urdu-video-editor

# Download all files:
# - app.py
# - video_processor.py
# - voice_generator.py
# - metadata_generator.py
# - requirements.txt
# - README.md
```

### Step 3: Create Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### Step-by-Step Workflow

#### 1. **Upload Video Clips**
   - Click "Choose video files" in the left panel
   - Select 5 or more video clips (MP4, AVI, MOV, MKV, FLV)
   - Each clip should be at least 5 seconds long
   - Recommended resolution: 1080p or 720p

#### 2. **Write Your Script**
   - Enter your Urdu script/story in the text area
   - The system accepts both Urdu and Roman Urdu
   - Example: "میرا نام علی ہے۔ میں ایک فلم بنا رہا ہوں۔"
   - Word count is displayed below the text area

#### 3. **Configure Settings**
   - **Voice Speed**: Adjust from 0.5x (slow) to 2.0x (fast)
   - **Video Quality**: Choose between 360p, 480p, 720p, 1080p
   - **Background Music**: Optional (toggle if needed)

#### 4. **Add Video Metadata**
   - **Title**: Give your video a catchy title
   - **Category**: Select from predefined categories
   - **Description**: Add a detailed description

#### 5. **Start Processing**
   - Click "🚀 Start Processing" button
   - Monitor progress through the status bar
   - Wait for all steps to complete:
     * 💾 Saving clips (10%)
     * 🎬 Combining videos (25%)
     * 🎙️ Generating voice (50%)
     * 🔊 Syncing audio (75%)
     * 🖼️ Generating thumbnail (85%)
     * 📝 Creating metadata (95%)
     * ✅ Complete (100%)

#### 6. **Download Results**
   - Preview video inline
   - View generated thumbnail
   - Download three files:
     * 📹 `final_video.mp4` - Complete edited video
     * 🖼️ `thumbnail.jpg` - YouTube thumbnail
     * 📋 `metadata.json` - Video metadata

## 📁 Project Structure

```
urdu-video-editor/
├── app.py                      # Main Streamlit application
├── video_processor.py          # Video processing & combining
├── voice_generator.py          # Text-to-speech & audio handling
├── metadata_generator.py       # Metadata & SEO optimization
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── venv/                       # Virtual environment (created after install)
```

## 🔧 Module Documentation

### `app.py` - Main Application
**Main Components:**
- File upload interface
- Script input area
- Configuration panel
- Processing orchestration
- Results display & download

**Key Functions:**
- `streamlit.file_uploader()` - Video clip upload
- `st.text_area()` - Script input
- `st.slider()` - Voice speed control
- Processing workflow management

### `video_processor.py` - Video Processing
**Class:** `VideoProcessor`

**Key Methods:**
```python
# Combine multiple video clips
combine_videos(video_paths, output_path, quality)

# Add audio track to video
add_audio_to_video(video_path, audio_path, output_path)

# Generate thumbnail from video frame
generate_thumbnail(video_path, output_path, frame_index)

# Get video duration
get_video_duration(video_path)

# Validate video file
validate_video(video_path)
```

### `voice_generator.py` - Voice Generation
**Class:** `VoiceGenerator`

**Key Methods:**
```python
# Generate Urdu voice-over
generate_voice(text, output_path, speed, pitch)

# Adjust audio playback speed
adjust_audio_speed(audio_path, output_path, speed)

# Add audio effects
add_audio_effects(audio_path, output_path, effect_type)

# Merge multiple audio files
merge_audio_files(audio_files, output_path, crossfade)

# Get audio duration
get_audio_duration(audio_path)
```

### `metadata_generator.py` - Metadata Generation
**Class:** `MetadataGenerator`

**Key Methods:**
```python
# Generate complete metadata
generate_metadata(title, description, category, duration, script)

# Generate YouTube-specific metadata
generate_youtube_metadata(title, description, tags, category)

# Create SRT subtitle file
create_srt_subtitle(script, duration, output_path)

# Export metadata to JSON
export_metadata_json(metadata, file_path)
```

## 📊 Output Files

### 1. **final_video.mp4**
- Complete edited video with voice-over
- Resolution: Based on quality selection
- Codec: H.264 video, AAC audio
- Format: MP4 (platform-compatible)

### 2. **thumbnail.jpg**
- YouTube-ready thumbnail (1280x720)
- First frame of video
- High quality JPEG

### 3. **metadata.json**
```json
{
  "video_id": "a1b2c3d4e5f6",
  "title": "Your Video Title",
  "description": "Full video description",
  "category": "تعلیم",
  "duration_seconds": 120,
  "duration_formatted": "02:00",
  "author": "Creator Name",
  "created_at": "2024-01-15T10:30:45",
  "keywords": ["keyword1", "keyword2"],
  "tags": ["tag1", "tag2"],
  "language": "Urdu",
  "seo": {
    "meta_title": "...",
    "meta_description": "...",
    "meta_keywords": "..."
  }
}
```

## ⚙️ Configuration Options

### Voice Speed
| Value | Effect |
|-------|--------|
| 0.5 | Very slow (2x slower) |
| 0.75 | Slow |
| 1.0 | Normal (default) |
| 1.5 | Fast |
| 2.0 | Very fast (2x faster) |

### Video Quality
| Quality | Resolution | File Size | Use Case |
|---------|-----------|-----------|----------|
| 360p | 640×360 | Small | Mobile/Web |
| 480p | 854×480 | Medium | Standard |
| 720p | 1280×720 | Large | HD/YouTube |
| 1080p | 1920×1080 | XL | 4K/Professional |

### Categories
```
علوم و تعلیم (Education)
تفریح (Entertainment)
خبریں (News)
ٹیکنالوجی (Technology)
دوسرہ (Other)
```

## 🎤 Urdu Language Support

### Text-to-Speech Engine
- **Primary**: pyttsx3 (offline, English with Urdu text)
- **Fallback 1**: Google Text-to-Speech (online, Urdu support)
- **Fallback 2**: Local pyttsx3 with male voice selection

### Supported Script Formats
✅ Native Urdu script (اردو)  
✅ Roman Urdu (Romanized)  
✅ Mixed Urdu/English text  

### Example Scripts
```
1. "میرا نام علی ہے۔ میں ایک ویڈیو بنا رہا ہوں۔"
2. "Mera naam Ali hai. Main ek video bana raha hoon."
3. "آپ کے لیے خصوصی معلومات۔ براہ کرم اگلی ویڈیو دیکھیں۔"
```

## 🐛 Troubleshooting

### Issue: "FFmpeg not found"
**Solution:**
```bash
# Windows
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg
```

### Issue: "No module named 'streamlit'"
**Solution:**
```bash
pip install -r requirements.txt
# or
pip install streamlit
```

### Issue: Voice-over not generating
**Solution:**
1. Check internet connection (gTTS requires internet)
2. Verify Urdu text is correctly formatted
3. Try different voice speed settings
4. Check available disk space

### Issue: Video combining is slow
**Solution:**
- Reduce video quality setting
- Use shorter clips
- Increase available RAM
- Close other applications

### Issue: "Permission denied" on Linux/Mac
**Solution:**
```bash
chmod +x app.py
python3 app.py
```

## 📈 Performance Tips

1. **Optimize Input Videos**
   - Pre-compress clips before uploading
   - Use consistent resolution
   - Test with 5-10 second clips first

2. **Improve Processing Speed**
   - Lower video quality during testing
   - Use 480p/720p instead of 1080p
   - Reduce script length for faster voice generation

3. **Better Audio Quality**
   - Use slower voice speed (0.8-0.9)
   - Write clear, concise scripts
   - Test voice generation separately

## 🔐 Security & Privacy

- All files processed locally on your machine
- No files uploaded to external servers (unless using gTTS)
- Temporary files automatically cleaned up
- Metadata stored locally in JSON format

## 📝 Example Usage Scenarios

### Scenario 1: Educational Content
```
Title: "اسلام میں سائنس" (Science in Islam)
Category: تعلیم (Education)
Clips: 7 clips of science experiments
Script: "خدا نے ہمیں عقل دی ہے..."
```

### Scenario 2: News Report
```
Title: "روز کی اہم خبریں" (Daily News)
Category: خبریں (News)
Clips: 10 clips of news footage
Script: "آج کی خبریں یہ ہیں..."
```

### Scenario 3: Entertainment
```
Title: "مضحکہ خیز پل" (Funny Moments)
Category: تفریح (Entertainment)
Clips: 8 funny video clips
Script: "دیکھیں یہ مضحکہ خیز لمحے..."
```

## 🎓 Learning Resources

### Streamlit Documentation
- Official Docs: https://docs.streamlit.io
- Video Tutorials: https://www.youtube.com/StreamlitIO

### OpenCV Documentation
- Official Docs: https://docs.opencv.org
- Python Bindings: https://opencv-python-tutroals.readthedocs.io

### FFmpeg Documentation
- Official Docs: https://ffmpeg.org
- Command Reference: https://ffmpeg.org/ffmpeg-all.html

## 📞 Support & Contact

For issues or feature requests:
1. Check troubleshooting section above
2. Review console error messages
3. Verify all dependencies are installed
4. Test with sample videos

## 📄 License

This project is provided as-is for educational and personal use.

## 🙏 Acknowledgments

Built for Pakistani content creators and Urdu speakers worldwide 🇵🇰

## 🎬 Sample Workflow

```
START
  ↓
Upload 5+ Video Clips
  ↓
Enter Urdu Script
  ↓
Configure Settings (Speed, Quality)
  ↓
Add Title & Description
  ↓
Click "Start Processing"
  ↓
[Video Processing]
  → Combine Clips
  → Generate Voice-Over
  → Sync Audio
  → Create Thumbnail
  → Generate Metadata
  ↓
Download Results
  → final_video.mp4
  → thumbnail.jpg
  → metadata.json
  ↓
END
```

## 🚀 Next Steps

1. **Test with sample videos**
   - Create test clips or download samples
   - Write a short Urdu script
   - Process and review output

2. **Customize for your needs**
   - Modify category names
   - Add background music support
   - Enhance subtitle generation

3. **Deploy online**
   - Use Streamlit Cloud
   - Deploy with Docker
   - Integration with web servers

## ✨ Version History

**v1.0** (Current)
- Initial release
- Core video editing features
- Urdu voice-over support
- Metadata generation
- Thumbnail creation

---

**Made with ❤️ for Urdu content creators**

Last Updated: January 2024  
Version: 1.0  
Status: Fully Functional
