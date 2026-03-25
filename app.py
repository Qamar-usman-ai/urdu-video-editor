import streamlit as st
import os
import asyncio
import edge_tts
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
import google.generativeai as genai
from openai import OpenAI

# --- API Configuration ---
# Gemini Configuration
GEMINI_API_KEY = st.sidebar.text_input("Enter Gemini API Key:", type="password")
# Grok is OpenAI-compatible
GROK_API_KEY = st.sidebar.text_input("Enter Grok API Key:", type="password")

def get_ai_metadata(script, provider):
    """Generates Title and Description using selected Free AI model."""
    prompt = f"Based on this Urdu story script: '{script}', generate a catchy Video Title and a short SEO description in Urdu. Keep it simple and natural."
    
    try:
        if provider == "Gemini (Free Tier)":
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-3-flash')
            response = model.generate_content(prompt)
            return response.text
        
        elif provider == "Grok (xAI)":
            client = OpenAI(api_key=GROK_API_KEY, base_url="https://api.x.ai/v1")
            response = client.chat.completions.create(
                model="grok-4.20-beta",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
    except Exception as e:
        return f"Error with {provider}: {str(e)}"

async def generate_voiceover(text, output_path):
    """Generates a Male Urdu voiceover using Edge TTS (Asad)."""
    communicate = edge_tts.Communicate(text, "ur-PK-AsadNeural")
    await communicate.save(output_path)

def process_video(video_paths, voice_path, output_path):
    """Merges clips and applies the Urdu voiceover."""
    clips = [VideoFileClip(v) for v in video_paths]
    final_clip = concatenate_videoclips(clips, method="compose")
    
    audio_background = AudioFileClip(voice_path)
    # Sync audio length to video
    final_audio = audio_background.set_duration(final_clip.duration)
    final_clip = final_clip.set_audio(final_audio)
    
    final_clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
    
    for c in clips: c.close()

# --- Streamlit Interface ---
st.set_page_config(page_title="Urdu Video Forge", layout="wide")
st.title("🎥 Urdu Video Forge")
st.markdown("### Mix Clips + Urdu Male Voice + AI Metadata")

# Selection for AI Provider
ai_provider = st.selectbox("Select AI Model for Metadata:", ["Gemini (Free Tier)", "Grok (xAI)"])

with st.container():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_videos = st.file_uploader("Upload 5+ Video Clips", type=["mp4", "mov"], accept_multiple_files=True)
        script_text = st.text_area("Write your Urdu story/script here:", height=200)
    
    with col2:
        if st.button("🚀 Start Production"):
            if not uploaded_videos or not script_text:
                st.warning("Please upload videos and write a script first.")
            elif not GEMINI_API_KEY and ai_provider == "Gemini (Free Tier)":
                st.error("Please enter Gemini API Key in the sidebar.")
            elif not GROK_API_KEY and ai_provider == "Grok (xAI)":
                st.error("Please enter Grok API Key in the sidebar.")
            else:
                if not os.path.exists("temp"): os.makedirs("temp")
                
                with st.status("Working on your video...") as status:
                    # 1. Save Files
                    v_paths = []
                    for i, v in enumerate(uploaded_videos):
                        p = f"temp/c{i}.mp4"
                        with open(p, "wb") as f: f.write(v.getbuffer())
                        v_paths.append(p)
                    
                    # 2. TTS
                    st.write("🎙️ Generating Male Urdu Voice...")
                    voice_p = "temp/v.mp3"
                    asyncio.run(generate_voiceover(script_text, voice_p))
                    
                    # 3. Video Edit
                    st.write("🎬 Editing and Merging Clips...")
                    out_p = "temp/final.mp4"
                    process_video(v_paths, voice_p, out_p)
                    
                    # 4. AI Metadata
                    st.write(f"🤖 Fetching metadata from {ai_provider}...")
                    metadata = get_ai_metadata(script_text, ai_provider)
                    
                    # 5. Thumbnail
                    final_v = VideoFileClip(out_p)
                    thumb_p = "temp/thumb.jpg"
                    final_v.save_frame(thumb_p, t=0.5)
                    
                    status.update(label="All Done!", state="complete")
                
                st.divider()
                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.video(out_p)
                    with open(out_p, "rb") as f:
                        st.download_button("📥 Download Video", f, "final_video.mp4")
                
                with res_col2:
                    st.image(thumb_p, caption="Generated Thumbnail")
                    st.subheader("Generated Title & Description")
                    st.write(metadata)
