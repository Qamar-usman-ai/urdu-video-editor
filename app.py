import streamlit as st
import os
import asyncio
import edge_tts
import math
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, vfx, TextClip, CompositeVideoClip
import google.generativeai as genai
from openai import OpenAI
from moviepy.config import change_settings

# --- Setup Directories & Config ---
TEMP_DIR = "temp_assets"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Configure ImageMagick path if you are on Windows and getting an error
# change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.0-Q16-HDRI\magick.exe"})

def split_text_into_sentences(text):
    """Splits Urdu text into individual sentences based on periods (.)"""
    sentences = text.split('.')
    # Clean up empty strings or extra whitespace
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

async def generate_voice_segment(text, path):
    """Generates Male Urdu voice (Asad) at a natural storytelling rate."""
    communicate = edge_tts.Communicate(text, "ur-PK-AsadNeural", rate="-5%")
    await communicate.save(path)

def get_subtitle_clip(text, duration, size):
    """Creates an Urdu subtitle overlay for a specific duration."""
    # Settings for professional subtitles
    subtitle = TextClip(
        text, 
        font='Arial',       # Use a font that supports Urdu (e.g., Noto Nastaliq Urdu)
        fontsize=45,        # Adjust size based on your video resolution
        color='white',      # Standard color
        bg_color='black',   # Adds a background bar for readability
        size=(size[0]*0.8, None), # 80% width of the video, auto height
        method='caption'    # Wraps text to multiple lines automatically
    ).set_duration(duration).set_position(('center', 'bottom')) # Centered at the bottom
    
    return subtitle

def create_synced_video_with_subs(video_paths, script, output_path):
    """Matches each clip to its corresponding script sentence with subtitles."""
    
    # 1. Prepare segments
    num_clips = len(video_paths)
    script_segments = split_text_into_sentences(script)
    
    # Ensure we have a script segment for every clip (repeat the last if necessary)
    while len(script_segments) < num_clips:
        script_segments.append(script_segments[-1])
    
    # Use only as many segments as we have clips
    script_segments = script_segments[:num_clips]
    
    final_composite_segments = []
    
    for i in range(num_clips):
        st.write(f"Processing Scene {i+1}: {script_segments[i]}...")
        
        # 2. Generate audio for this specific sentence
        seg_audio_path = os.path.join(TEMP_DIR, f"audio_{i}.mp3")
        asyncio.run(generate_voice_segment(script_segments[i], seg_audio_path))
        seg_audio = AudioFileClip(seg_audio_path)
        seg_audio_dur = seg_audio.duration
        
        # 3. Load the clip and calculate speed factor
        clip = VideoFileClip(video_paths[i])
        speed_factor = clip.duration / seg_audio_dur
        
        # 4. Stretch/Slow the clip and attach audio
        synced_clip = clip.fx(vfx.speedx, speed_factor).set_audio(seg_audio)
        
        # 5. GENERATE SUBTITLE CLIP
        subtitle_clip = get_subtitle_clip(script_segments[i], seg_audio_dur, clip.size)
        
        # 6. Overlay subtitle onto the clip
        final_clip = CompositeVideoClip([synced_clip, subtitle_clip])
        final_composite_segments.append(final_clip)

    # 7. Concatenate all perfectly synced, subtitled segments
    st.write("Merging all scenes into final video...")
    final_video_sequence = concatenate_videoclips(final_composite_segments, method="compose")
    
    # Write file (this will combine video, audio, and subtitles)
    final_video_sequence.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
    
    # Cleanup resources
    for c in final_composite_segments: c.close()

# --- Streamlit UI ---
st.set_page_config(page_title="Pro Urdu Sub Studio", layout="wide")
st.title("🎬 Pro Urdu Video Sync & Sub Studio")
st.markdown("I will create a perfectly synced, subtitled Urdu video with a natural Male voice (Asad).")

with st.sidebar:
    st.header("AI Config")
    ai_model = st.selectbox("Metadata AI", ["Gemini 3 Flash", "Grok (xAI)"])
    gem_key = st.text_input("Gemini Key", type="password")
    gro_key = st.text_input("Grok Key", type="password")
    st.info("I will split your script into sentences to create the subtitles automatically.")

col1, col2 = st.columns(2)

with col1:
    v_files = st.file_uploader("Upload 5-6 Video Clips (Must be in correct order)", type=["mp4", "mov"], accept_multiple_files=True)
    
with col2:
    example_urdu_script = """یہ کہانی ہے علی کی۔ ایک عام سے مگر خواب دیکھنے والے لڑکے کی۔
چھوٹے سے شہر میں پیدا ہونے والا یہ لڑکا جب بھی آسمان کی طرف دیکھتا، اس کی آنکھوں میں ایک خواب چمکتا تھا۔
ایک خواب جو کہنے والوں کو ہنسی آتی تھی۔
وہ خواب تھا... پاکستان کا CSS آفیسر بننا۔ اپنے والدین کا نام روشن کرنا۔ اِس ملک کی خدمت کرنا۔
یہ خواب اس کے دل میں اتنا گہرا تھا کہ وہ رات دن اس کی تعبیر کی تلاش میں رہتا۔"""
    script_input = st.text_area("Paste Complete Urdu Story (Separate sentences with '.'):", value=example_urdu_script, height=250)

if st.button("🚀 Generate Final Subtitled Video"):
    if not v_files or not script_input:
        st.error("Please provide both clips and script.")
    else:
        with st.status("Building your video story with subtitles...") as status:
            # Save Raw Clips
            paths = []
            for i, f in enumerate(v_files):
                p = os.path.join(TEMP_DIR, f"raw_{i}.mp4")
                with open(p, "wb") as out: out.write(f.getbuffer())
                paths.append(p)
            
            # Start Perfect Sync & Subtitle Generation
            out_v_file = os.path.join(TEMP_DIR, "synced_subs_final.mp4")
            create_synced_video_with_subs(paths, script_input, out_v_file)
            
            status.update(label="Video Creation Complete!", state="complete")

        st.divider()
        st.video(out_v_file)
        with open(out_v_file, "rb") as f:
            st.download_button("Download Subtitled Video", f, "pro_urdu_story.mp4")
