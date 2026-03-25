# 🔧 Troubleshooting Guide

## Installation Issues

### Problem: "Python is not installed"

**Error Message:**
```
'python' is not recognized as an internal or external command
```

**Solutions:**
1. Download Python from https://www.python.org
2. During installation, CHECK "Add Python to PATH"
3. Restart your computer
4. Verify: `python --version`

---

### Problem: "FFmpeg not found"

**Error Message:**
```
FFmpeg is not installed or not in PATH
```

**Solutions:**

**Windows (Using Chocolatey):**
```powershell
# Install Chocolatey first if not installed
# https://chocolatey.org/install

choco install ffmpeg
```

**Windows (Manual):**
1. Download from: https://ffmpeg.org/download.html
2. Extract to: `C:\ffmpeg`
3. Add to PATH:
   - Right-click "This PC" → Properties
   - Advanced system settings
   - Environment Variables
   - Add `C:\ffmpeg\bin` to PATH
4. Restart computer
5. Verify: `ffmpeg -version`

**macOS:**
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg
brew install ffmpeg

# Verify
ffmpeg -version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg

# Verify
ffmpeg -version
```

---

### Problem: "pip install fails"

**Error Message:**
```
ModuleNotFoundError: No module named 'pip'
```

**Solutions:**
```bash
# Try pip3 instead
pip3 install -r requirements.txt

# Or upgrade pip first
python -m pip install --upgrade pip
pip install -r requirements.txt

# Or use Python directly
python -m pip install streamlit opencv-python numpy scipy pyttsx3
```

---

### Problem: "Virtual environment issues"

**Error Message:**
```
ModuleNotFoundError or version conflicts
```

**Solutions:**
```bash
# Remove old environment
rmdir /s venv  # Windows
rm -rf venv    # Mac/Linux

# Create fresh environment
python -m venv venv

# Activate it
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install fresh
pip install -r requirements.txt
```

---

## Runtime Issues

### Problem: "Streamlit not found"

**Error Message:**
```
No module named 'streamlit'
```

**Solutions:**
```bash
# Make sure venv is activated
# Windows
venv\Scripts\activate

# Then install
pip install streamlit
```

---

### Problem: "cv2 (OpenCV) module missing"

**Error Message:**
```
No module named 'cv2'
```

**Solutions:**
```bash
# Install OpenCV
pip install opencv-python opencv-contrib-python

# If still failing
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python-headless  # For servers
```

---

### Problem: "App won't start - Port already in use"

**Error Message:**
```
Port 8501 is already in use
```

**Solutions:**
```bash
# Use different port
streamlit run app.py --server.port 8502

# Or kill process using port
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :8501
kill -9 <PID>
```

---

## Video Processing Issues

### Problem: "Video upload fails"

**Error Message:**
```
File not recognized as video
Error reading video metadata
```

**Solutions:**
1. **Check file format:** Only MP4, AVI, MOV, MKV, FLV supported
2. **Use FFmpeg to convert:**
   ```bash
   ffmpeg -i input.mkv -c:v libx264 -c:a aac output.mp4
   ```
3. **Reduce file size:**
   ```bash
   ffmpeg -i large_video.mp4 -vf scale=1280:720 -c:v libx264 -crf 23 small_video.mp4
   ```
4. **Check video integrity:**
   ```bash
   ffmpeg -v error -i video.mp4 -f null -
   ```

---

### Problem: "Minimum 5 clips required warning"

**Solution:**
You need at least 5 video clips. If you have fewer:
- Create shorter clips by splitting videos
- Record additional clips
- Download sample videos online

---

### Problem: "Video file too large"

**Error Message:**
```
File size exceeds maximum limit
```

**Solution:**
Compress videos before uploading:
```bash
# Basic compression
ffmpeg -i input.mp4 -vf scale=1280:720 -c:v libx264 -crf 23 -preset fast output.mp4

# High compression
ffmpeg -i input.mp4 -vf scale=854:480 -c:v libx264 -crf 28 -preset slow output.mp4
```

**Quality vs Compression:**
- CRF 18-23: High quality
- CRF 23-28: Balanced
- CRF 28-36: Small size

---

### Problem: "Video combining is very slow"

**Solutions:**
1. **Reduce quality setting:** Use 480p instead of 1080p
2. **Use shorter videos:** Process 5-10 second clips
3. **Increase available RAM:** Close other applications
4. **Change FFmpeg preset:**
   - Edit `config.py`
   - Change `"preset": "medium"` to `"preset": "fast"`

---

## Audio & Voice Issues

### Problem: "Voice-over not generating"

**Error Message:**
```
pyttsx3 initialization failed
No audio output
```

**Solutions:**
```bash
# Install required package
pip install pyttsx3

# Or use Google TTS (needs internet)
pip install gtts

# Test voice generation
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('Hello'); engine.runAndWait()"
```

**For Urdu:**
- System must support Urdu fonts
- Try with shorter text first
- Ensure internet for gTTS

---

### Problem: "Urdu text not pronounced correctly"

**Solutions:**
1. **Check text encoding:** Ensure file is UTF-8
2. **Use proper Urdu script:** Not Roman Urdu for pyttsx3
3. **Use gTTS:** Better Urdu support
4. **Try slower speed:** 0.8 or 0.9 instead of 1.0

---

### Problem: "Audio too quiet or too loud"

**Solutions:**
1. **Adjust voice speed:** Slower = more natural volume
2. **Edit config.py:**
   ```python
   VOICE_SETTINGS = {
       "volume": 1.5  # Increase from 1.0
   }
   ```
3. **Post-process audio:** Add normalization

---

### Problem: "Audio and video out of sync"

**Solutions:**
1. **Check audio duration:** Should match or be shorter than video
2. **Re-run processing:** Sometimes fixes timing
3. **Manual sync:** Use separate audio editor

---

## File & Metadata Issues

### Problem: "Output files not found"

**Error Message:**
```
Cannot download file - file not found
```

**Solutions:**
1. **Check temp directory:**
   - Windows: `C:\Users\YourName\.urdu-video-editor\output\`
   - Mac: `~/.urdu-video-editor/output/`
   - Linux: `~/.urdu-video-editor/output/`

2. **Create directories manually:**
   ```bash
   mkdir -p ~/.urdu-video-editor/output
   ```

3. **Check file permissions:**
   ```bash
   # Mac/Linux
   chmod 755 ~/.urdu-video-editor
   chmod 755 ~/.urdu-video-editor/output
   ```

---

### Problem: "Thumbnail not generated"

**Solutions:**
1. Check video duration is > 1 second
2. Verify video file is valid:
   ```bash
   ffmpeg -v error -i video.mp4 -f null -
   ```
3. Try manual generation:
   ```python
   from video_processor import VideoProcessor
   vp = VideoProcessor()
   vp.generate_thumbnail('video.mp4', 'thumb.jpg', frame_index=2)
   ```

---

### Problem: "Invalid metadata JSON"

**Solutions:**
1. Ensure title and description contain valid UTF-8 Urdu
2. Check for special characters causing JSON errors
3. Validate JSON:
   ```bash
   python -m json.tool metadata.json
   ```

---

## Performance Issues

### Problem: "Processing takes very long"

**Time Estimates:**
- 5 clips, 5 seconds each = 1-2 minutes
- 10 clips, 10 seconds each = 3-5 minutes
- 15 clips, 15 seconds each = 7-10 minutes

**To Speed Up:**
1. Use lower video quality (360p or 480p)
2. Reduce script length
3. Use shorter video clips
4. Close other applications
5. Increase available RAM

---

### Problem: "Computer crashes during processing"

**Solutions:**
1. **Increase virtual memory:**
   - Windows: Settings → System → About → Advanced system settings
   - Set virtual memory to 4-8GB

2. **Reduce simultaneous processing:**
   - Process fewer clips at once
   - Use lower quality

3. **Monitor resources:**
   - Windows: Task Manager
   - Mac: Activity Monitor
   - Linux: `top` or `htop`

---

### Problem: "Out of disk space"

**Solutions:**
```bash
# Clear temporary files
# Windows
del %USERPROFILE%\.urdu-video-editor\temp\*

# Mac/Linux
rm -rf ~/.urdu-video-editor/temp/*

# Or delete entire temp directory (will be recreated)
rmdir /s .urdu-video-editor\temp  # Windows
rm -rf ~/.urdu-video-editor/temp  # Mac/Linux
```

---

## Error Messages Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError` | Package not installed | `pip install package_name` |
| `FileNotFoundError` | File doesn't exist | Check file path |
| `PermissionError` | No write access | Check folder permissions |
| `TimeoutError` | Process too slow | Reduce quality/clip size |
| `FFmpegError` | FFmpeg issue | Reinstall FFmpeg |
| `ValueError: empty sequence` | No video clips | Upload at least 5 clips |
| `AVError` | Video codec issue | Convert video format |
| `AssertionError` | Validation failed | Check input parameters |

---

## Debug Mode

### Enable Verbose Logging

Edit `app.py` and add:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

Then check console output for detailed error messages.

---

### Collect Debug Information

```bash
# System info
python -c "import sys; print(sys.version)"

# Installed packages
pip list

# FFmpeg version
ffmpeg -version

# Python packages
python -c "import cv2, streamlit; print(cv2.__version__, streamlit.__version__)"
```

---

## Test Individual Components

```python
# Test video processing
from video_processor import VideoProcessor
vp = VideoProcessor()
print(vp.validate_video('your_video.mp4'))

# Test voice generation
from voice_generator import VoiceGenerator
vg = VoiceGenerator()
vg.generate_voice("السلام عليكم", "test.wav", speed=1.0)

# Test metadata
from metadata_generator import MetadataGenerator
mg = MetadataGenerator()
meta = mg.generate_metadata("Title", "Description", "Category", 60, "Script")
print(meta)
```

---

## Getting Help

### Before Asking for Help
1. ✅ Check this troubleshooting guide
2. ✅ Read README.md
3. ✅ Check console error messages
4. ✅ Try restarting the app
5. ✅ Verify all dependencies installed

### When Reporting Issues
Include:
- Complete error message
- Operating system
- Python version
- FFmpeg version
- Steps to reproduce
- Sample video/script

---

## FAQ

**Q: Can I use videos recorded on my phone?**
A: Yes! Export as MP4 and upload.

**Q: What's the maximum video length?**
A: No hard limit, but processing gets slower. Test with 1-2 minute videos first.

**Q: Can I use English instead of Urdu?**
A: Yes, but voice quality may vary. Primary support is Urdu.

**Q: Can I edit after processing?**
A: Yes, use any video editor (DaVinci Resolve, Adobe Premiere, etc.)

**Q: Is internet required?**
A: Only for Google TTS voice generation. Pyttsx3 works offline.

**Q: Can I use this commercially?**
A: Yes, but test functionality first.

---

## Version-Specific Issues

**Python 3.8:** 
- Works fine, but 3.9+ recommended

**Python 3.12+:**
- Some older packages may not work
- Use Python 3.9-3.11 recommended

---

Made with ❤️ for troubleshooting support 🇵🇰

Last Updated: January 2024  
Version: 1.0
