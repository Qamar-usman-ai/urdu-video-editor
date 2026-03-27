import streamlit as st
import os
import asyncio
import edge_tts
import math
import re
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, vfx, TextClip, CompositeVideoClip

# --- Setup Directories ---
TEMP_DIR = "temp_assets"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def split_text_into_sentences(text):
    """Splits Urdu text into sentences correctly."""
    # Using a safer split for Python 3.14 compatibility
    sentences = re.split(r'[.\u06d4]', text) 
    return [s.strip() for s in sentences if s.strip()]

async def generate_voice_segment(text, path):
    """Generates Male Urdu voice."""
    communicate = edge_tts.Communicate(text, "ur-PK-AsadNeural", rate="-5%")
    await communicate.save(path)

def get_subtitle_clip(text, duration, size):
    """Creates a subtitle overlay compatible with Linux/Streamlit Cloud."""
    try:
        # We use 'Caption' method which is more stable on cloud servers
        subtitle = TextClip(
            text, 
            font='Liberation-Sans', # Standard Linux font
            fontsize=40,
            color='white',
            bg_color='black',
            size=(size[0] * 0.9, None),
            method='caption'
        ).set_duration(duration).set_position(('center', 'bottom'))
        return subtitle
    except Exception as e:
        st.error(f"Subtitle Error: {e}. Ensure packages.txt has 'imagemagick'.")
        return None

def create_synced_video_with_subs(video_paths, script, output_path):
    script_segments = split_text_into_sentences(script)
    num_clips = len(video_paths)
    
    # Sync segments to clips
    while len(script_segments) < num_clips:
        script_segments.append(script_segments[-1] if script_segments else "...")
    script_segments = script_segments[:num_clips]
    
    final_composite_segments = []
    
    for i in range(num_clips):
        seg_audio_path = os.path.join(TEMP_DIR, f"audio_{i}.mp3")
        asyncio.run(generate_voice_segment(script_segments[i], seg_audio_path))
        
        audio = AudioFileClip(seg_audio_path)
        clip = VideoFileClip(video_paths[i])
        
        # Calculate speed to match audio exactly
        speed_factor = clip.duration / audio.duration
        synced_clip = clip.fx(vfx.speedx, speed_factor).set_audio(audio)
        
        # Add Subtitles
        sub = get_subtitle_clip(script_segments[i], audio.duration, clip.size)
        
        if sub:
            final_segment = CompositeVideoClip([synced_clip, sub])
        else:
            final_segment = synced_clip
            
        final_composite_segments.append(final_segment)

    st.write("Merging and Exporting Final Video...")
    final_video = concatenate_videoclips(final_composite_segments, method="compose")
    
    # Write to file
    final_video.write_videofile(
        output_path, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac",
        temp_audiofile=os.path.join(TEMP_DIR, 'temp-audio.m4a'),
        remove_temp=True
    )
    
    # Resource Management
    for c in final_composite_segments: c.close()

# --- Streamlit Interface ---
st.title("🎬 Urdu Story Pro (Sync + Subs)")

col1, col2 = st.columns(2)
with col1:
    v_files = st.file_uploader("Upload 5+ Clips", type=["mp4", "mov"], accept_multiple_files=True)
with col2:
    script_input = st.text_area("Urdu Story (Use . to separate sentences):", height=200)

if st.button("🚀 Start Production"):
    if v_files and script_input:
        with st.status("Processing...") as status:
            # 1. Save
            paths = []
            for i, f in enumerate(v_files):
                p = os.path.join(TEMP_DIR, f"v_{i}.mp4")
                with open(p, "wb") as out: out.write(f.getbuffer())
                paths.append(p)
            
            # 2. Process
            final_out = os.path.join(TEMP_DIR, "final_story.mp4")
            create_synced_video_with_subs(paths, script_input, final_out)
            status.update(label="Complete!", state="complete")
            
        st.video(final_out)
        with open(final_out, "rb") as f:
            st.download_button("Download Video", f, "story.mp4")
