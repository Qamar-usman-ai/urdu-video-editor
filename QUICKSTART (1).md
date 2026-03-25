# 🚀 Quick Start Guide - 5 Minutes Setup

## Installation (5 steps)

### Step 1: Download & Extract
1. Download all files from the project
2. Extract to a folder: `C:\urdu-video-editor` (Windows)
3. Or on Mac/Linux: `~/urdu-video-editor`

### Step 2: Install FFmpeg (Choose Your OS)

**🪟 Windows:**
```
Option A - Using Chocolatey:
choco install ffmpeg

Option B - Manual Download:
Visit: https://ffmpeg.org/download.html
Download Windows build and add to System PATH
```

**🍎 macOS:**
```bash
brew install ffmpeg
```

**🐧 Linux (Ubuntu/Debian):**
```bash
sudo apt-get install ffmpeg
```

### Step 3: Open Command Prompt/Terminal
1. Navigate to your project folder
2. Windows: `cd C:\urdu-video-editor`
3. Mac/Linux: `cd ~/urdu-video-editor`

### Step 4: Install Python Packages
```bash
pip install -r requirements.txt
```

### Step 5: Run the App
```bash
streamlit run app.py
```

✅ App opens in your browser at http://localhost:8501

---

## First Video (10 Minutes)

### 1️⃣ Prepare Your Videos
- Record or find 5+ video clips (5-15 seconds each)
- Save as MP4, AVI, or MOV format
- Keep them on your computer

### 2️⃣ Start the App
```bash
streamlit run app.py
```

### 3️⃣ Upload Videos
1. Click "Choose video files"
2. Select all 5+ video clips
3. Wait for upload (shows file size)

### 4️⃣ Write Your Story in Urdu
Copy & paste this example:
```
میرا نام علی ہے۔
میں ایک کریٹر ہوں۔
میں اردو میں ویڈیو بناتا ہوں۔
```

### 5️⃣ Set Options
- **Voice Speed**: 1.0 (normal)
- **Quality**: 720p
- **Title**: "میری پہلی ویڈیو"
- **Category**: "دوسرہ"

### 6️⃣ Click "Start Processing"
- Monitor the progress bar
- Takes 2-5 minutes depending on video length

### 7️⃣ Download Your Video
- Click "📹 Download Video"
- Get `final_video.mp4`
- Also save thumbnail & metadata

---

## System Requirements Checklist

- [ ] Python 3.8+ installed
- [ ] FFmpeg installed
- [ ] 4GB+ RAM
- [ ] 5GB free hard drive space
- [ ] 5+ video clips ready
- [ ] Urdu script written

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "FFmpeg not found" | Install FFmpeg (see Step 2 above) |
| "pip install fails" | Use `pip3` instead or upgrade pip: `pip install --upgrade pip` |
| "Streamlit not found" | Run: `pip install streamlit` |
| "Voice not generating" | Check internet (gTTS needs connection) |
| "Processing too slow" | Lower quality to 480p or use shorter clips |

---

## Example Scripts

### 📚 Educational Video
```
اسلام میں سائنس کا کردار بہت اہم ہے۔
قرآن میں بہت سی سائنسی حقائق ہیں۔
ہم سائنس کو سمجھ کر عبادت کریں۔
```

### 🎬 Entertainment Video
```
آج میں آپ کو کچھ مضحکہ خیز لمحے دکھاتا ہوں۔
یہ ویڈیو آپ کو ضرور ہنسائے گی۔
براہ کرم شیئر کریں اور سبسکرائب کریں۔
```

### 📰 News Video
```
آج کی اہم خبریں یہ ہیں:
پہلی خبر: ...
دوسری خبر: ...
تیسری خبر: ...
```

---

## Tips for Best Results

### 📹 Video Quality
- Use HD videos (720p or 1080p)
- Consistent lighting
- Clear audio (for background)
- Steady camera or tripod

### 🎙️ Voice Quality
- Slow down voice (0.8-0.9) for clarity
- Write clear, simple sentences
- Avoid very long paragraphs
- Use proper Urdu punctuation

### 📊 Editing Quality
- 5-10 video clips = ~1-2 minutes video
- Balance short & long clips
- Match clips to script meaning
- Add variety in angles

---

## File Locations

After processing, files saved in:

**Windows:** `C:\Users\YourName\.urdu-video-editor\output\`

**Mac:** `~/.urdu-video-editor/output/`

**Linux:** `~/.urdu-video-editor/output/`

---

## Next Steps

1. ✅ Create your first video (follow above)
2. 📚 Read full README.md for advanced features
3. 🎓 Explore configuration options in config.py
4. 🚀 Upload to YouTube or social media
5. 💡 Experiment with different voice speeds
6. 🎨 Customize metadata for SEO

---

## Video Processing Flow

```
YOUR VIDEOS + URDU SCRIPT
         ↓
   [Upload Section]
         ↓
   [Configuration]
         ↓
   START PROCESSING
         ↓
   🎬 Combine Videos (10%)
         ↓
   🎙️ Generate Voice (40%)
         ↓
   🔊 Add Audio (20%)
         ↓
   🖼️ Thumbnail (10%)
         ↓
   📝 Metadata (10%)
         ↓
   ✅ DOWNLOAD RESULTS
```

---

## Contact & Support

### Errors or Issues?
1. Check console for error messages
2. Verify all files are in correct folder
3. Try restarting the app
4. Delete temp files: `.urdu-video-editor\temp\`

### Need Help?
- Read README.md for detailed documentation
- Check video_processor.py docstrings
- Review config.py for all settings

---

## Success Checklist

- [ ] FFmpeg installed
- [ ] Python packages installed
- [ ] App runs without errors
- [ ] Can upload video clips
- [ ] Can write Urdu script
- [ ] Processing completes
- [ ] Can download final video
- [ ] Final video plays correctly
- [ ] Thumbnail looks good
- [ ] Metadata is complete

---

## Next Advanced Features

Future versions will include:
- 🎵 Background music support
- 📝 Automatic subtitles
- 🎬 Video transitions
- ✨ Special effects
- 💬 Multiple voice options
- 🌍 Multiple language support
- 🖼️ Custom watermarks

---

Made with ❤️ for Urdu content creators 🇵🇰

**Version:** 1.0  
**Last Updated:** January 2024  
**Status:** Fully Functional & Ready to Use
