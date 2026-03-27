import streamlit as st
import os
import asyncio
import edge_tts
import math
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, vfx, CompositeAudioClip
import google.generativeai as genai
from openai import OpenAI

# --- Setup ---
TEMP_DIR = "temp_output"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def split_text(text, n):
    """Splits the Urdu script into 'n' equal parts to match the number of clips."""
    words = text.split()
    total_words = len(words)
    size = math.ceil(total_words / n)
    return [" ".join(words[i:i + size]) for i in range(0, total_words, size)]

async def generate_voice_segment(text, path):
    """Generates the highest quality Male Urdu voice (Asad)."""
    # We use a slightly slower rate (-5%) for better clarity in storytelling
    communicate = edge_tts.Communicate(text, "ur-PK-AsadNeural", rate="-5%")
    await communicate.save(path)

def create_synced_video(video_paths, script, output_path):
    """Matches each clip to a specific part of the script for perfect timing."""
    num_clips = len(video_paths)
    script_parts = split_text(script, num_clips)
    
    final_segments = []
    
    for i in range(num_clips):
        st.write(f"Syncing Segment {i+1}...")
        
        # 1. Generate audio for this specific part of the story
        seg_audio_path = os.path.join(TEMP_DIR, f"audio_{i}.mp3")
        asyncio.run(generate_voice_segment(script_parts[i], seg_audio_path))
        seg_audio = AudioFileClip(seg_audio_path)
        
        # 2. Load the clip and calculate the speed factor
        clip = VideoFileClip(video_paths[i])
        # Speed = Original Duration / Target Duration
        speed_factor = clip.duration / seg_audio.duration
        
        # 3. Stretch/Slow the clip and attach its specific audio
        synced_clip = clip.fx(vfx.speedx, speed_factor).set_audio(seg_audio)
        final_segments.append(synced_clip)

    # 4. Concatenate all perfectly synced segments
    final_video = concatenate_videoclips(final_segments, method="compose")
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
    
    # Cleanup
    for c in final_segments: c.close()

# --- Streamlit Interface ---
st.set_page_config(page_title="Pro Urdu Video Sync", layout="wide")
st.title("🎬 Pro Urdu Video Sync")
st.markdown("Each clip you upload will now match a specific part of your Urdu story.")

with st.sidebar:
    st.header("AI Config")
    ai_model = st.selectbox("Metadata AI", ["Gemini 3 Flash", "Grok (xAI)"])
    gem_key = st.text_input("Gemini Key", type="password")
    gro_key = st.text_input("Grok Key", type="password")

col1, col2 = st.columns(2)

with col1:
    files = st.file_uploader("Upload 5-6 Clips (Order matters!)", type=["mp4", "mov"], accept_multiple_files=True)
    
with col2:
    story_input = st.text_area("Paste Full Urdu Story:", height=300)

if st.button("🚀 Generate Synced Video"):
    if not files or not story_input:
        st.error("Please provide both clips and script.")
    else:
        with st.status("Processing Segments...") as status:
            # Save Raw Clips
            paths = []
            for i, f in enumerate(files):
                p = os.path.join(TEMP_DIR, f"raw_{i}.mp4")
                with open(p, "wb") as out: out.write(f.getbuffer())
                paths.append(p)
            
            # Start Segmented Syncing
            out_v = os.path.join(TEMP_DIR, "synced_final.mp4")
            create_synced_video(paths, story_input, out_v)
            
            status.update(label="Video Synced Successfully!", state="complete")

        st.divider()
        st.video(out_v)
        with open(out_v, "rb") as f:
            st.download_button("Download Synced Video", f, "final_urdu_story.mp4")
