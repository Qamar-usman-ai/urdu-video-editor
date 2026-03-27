import streamlit as st
import os
import asyncio
import edge_tts
import math
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, vfx, CompositeAudioClip
import google.generativeai as genai

# --- Setup Directories ---
TEMP_DIR = "temp_output"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# --- Helper Functions ---

def split_text(text, n):
    """Splits the Urdu script into 'n' equal parts to match the number of clips."""
    words = text.split()
    total_words = len(words)
    if total_words == 0: return [""] * n
    size = math.ceil(total_words / n)
    return [" ".join(words[i:i + size]) for i in range(0, total_words, size)]

async def generate_voice_segment(text, path):
    """Generates a high-energy, motivational Urdu voice (Asad)."""
    # volume="+50%" and pitch="+10Hz" makes the voice sound stronger and more professional
    communicate = edge_tts.Communicate(
        text, 
        "ur-PK-AsadNeural", 
        rate="-5%", 
        volume="+50%", 
        pitch="+10Hz"
    )
    await communicate.save(path)

def create_synced_video(video_paths, script, output_path):
    """Matches each clip to a specific part of the script with background music mixing."""
    num_clips = len(video_paths)
    script_parts = split_text(script, num_clips)
    
    final_segments = []
    
    for i in range(num_clips):
        st.write(f"🔄 Processing Segment {i+1} of {num_clips}...")
        
        # 1. Generate High-Energy AI Voice for this segment
        seg_audio_path = os.path.join(TEMP_DIR, f"audio_{i}.mp3")
        asyncio.run(generate_voice_segment(script_parts[i], seg_audio_path))
        ai_voice = AudioFileClip(seg_audio_path).volumex(1.4) # Boost voice volume
        
        # 2. Load the clip and calculate the speed factor to match audio length
        clip = VideoFileClip(video_paths[i])
        # Speed = Original Duration / Target (Audio) Duration
        speed_factor = clip.duration / ai_voice.duration
        
        # 3. Stretch/Slow the clip visually
        synced_clip = clip.fx(vfx.speedx, speed_factor)
        
        # 4. AUDIO MIXING: Keep original clip music but lower it (Ducking)
        if synced_clip.audio is not None:
            # Lower original music to 20% so the AI voice is the hero
            background_music = synced_clip.audio.volumex(0.2) 
            combined_audio = CompositeAudioClip([background_music, ai_voice])
        else:
            # If the clip has no sound, just use the AI voice
            combined_audio = ai_voice
            
        # 5. Attach the mixed audio to the synced clip
        synced_clip = synced_clip.set_audio(combined_audio).set_duration(ai_voice.duration)
        final_segments.append(synced_clip)

    # 6. Final Assembly
    st.write("🎬 Finalizing Video Render...")
    final_video = concatenate_videoclips(final_segments, method="compose")
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
    
    # Cleanup memory
    for c in final_segments: c.close()

# --- Streamlit Interface ---
st.set_page_config(page_title="Failure to Success | AI Video Factory", layout="wide")
st.title("🚀 Failure to Success: AI Video Factory")
st.markdown("Automate your Urdu storytelling by syncing professional AI voiceovers with your video clips.")

with st.sidebar:
    st.header("⚙️ Configuration")
    st.info("Ensure your clips have high-quality background music; this tool will automatically mix it with the AI voice.")
    if st.button("🧹 Clear Temp Files"):
        for f in os.listdir(TEMP_DIR):
            os.remove(os.path.join(TEMP_DIR, f))
        st.success("Cleared!")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Your Visuals")
    files = st.file_uploader("Upload 4-6 Clips (In Order)", type=["mp4", "mov"], accept_multiple_files=True)
    
with col2:
    st.subheader("2. Your Motivational Script")
    story_input = st.text_area("Paste your Urdu story here:", height=300, placeholder="مثال کے طور پر: ایلون مسک کی زندگی میں ایک وقت ایسا بھی آیا...")

if st.button("🔥 Generate Final Video"):
    if not files or not story_input:
        st.error("Missing Files or Script! Please provide both to continue.")
    else:
        try:
            with st.status("🛠️ Building your masterpiece...") as status:
                # Save Raw Clips to Temp Folder
                paths = []
                for i, f in enumerate(files):
                    p = os.path.join(TEMP_DIR, f"raw_{i}.mp4")
                    with open(p, "wb") as out: 
                        out.write(f.getbuffer())
                    paths.append(p)
                
                # Run the Video Creation Engine
                out_v = os.path.join(TEMP_DIR, "final_production.mp4")
                create_synced_video(paths, story_input, out_v)
                
                status.update(label="✅ Video Ready for Download!", state="complete")

            st.divider()
            st.video(out_v)
            with open(out_v, "rb") as f:
                st.download_button("📥 Download MP4 Video", f, "Failure_to_Success_Video.mp4")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
