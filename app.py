import streamlit as st
import os
import asyncio
import edge_tts
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
import google.generativeai as genai
from openai import OpenAI

# --- Setup Directories ---
if not os.path.exists("temp"):
    os.makedirs("temp")

# --- AI Functions ---
def get_ai_metadata(script, provider, gemini_key, grok_key):
    prompt = f"Based on this Urdu story script: '{script}', generate a catchy Video Title and a short SEO description in Urdu. Keep it simple and human-like."
    
    try:
        if provider == "Gemini 3 Flash":
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash') # Gemini 3 Flash equivalent
            response = model.generate_content(prompt)
            return response.text
        
        elif provider == "Grok (xAI)":
            client = OpenAI(api_key=grok_key, base_url="https://api.x.ai/v1")
            response = client.chat.completions.create(
                model="grok-beta",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"

async def generate_voiceover(text, output_path):
    """Generates a high-quality Male Urdu voiceover."""
    communicate = edge_tts.Communicate(text, "ur-PK-AsadNeural")
    await communicate.save(output_path)

def create_final_video(video_paths, voice_path, output_path):
    """Combines clips and loops them to match a long story."""
    clips = [VideoFileClip(v) for v in video_paths]
    audio = AudioFileClip(voice_path)
    audio_dur = audio.duration
    
    # Merge all uploaded clips into one sequence
    combined_clips = concatenate_videoclips(clips, method="compose")
    video_dur = combined_clips.duration
    
    # LOOP LOGIC: If story is longer than clips, repeat the clips
    if video_dur < audio_dur:
        loop_count = int(audio_dur // video_dur) + 1
        final_v = concatenate_videoclips([combined_clips] * loop_count)
    else:
        final_v = combined_clips
        
    # Trim to exact audio length and attach sound
    final_v = final_v.set_duration(audio_dur).set_audio(audio)
    
    # Write file (using high compatibility settings)
    final_v.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True)
    
    # Close clips to prevent memory errors
    for c in clips: c.close()
    combined_clips.close()

# --- Streamlit UI ---
st.set_page_config(page_title="Urdu Video Forge", page_icon="🎥")
st.title("🎥 Urdu Video Forge")
st.info("Upload clips and a story; I'll handle the rest with a Male Urdu Voice.")

# Sidebar for Keys
with st.sidebar:
    st.header("API Configuration")
    ai_choice = st.selectbox("Select Metadata AI", ["Gemini 3 Flash", "Grok (xAI)"])
    gemini_k = st.text_input("Gemini API Key", type="password")
    grok_k = st.text_input("Grok API Key", type="password")

# Main Interface
col1, col2 = st.columns([1, 1])

with col1:
    v_files = st.file_uploader("Upload Clips (Select multiple at once)", type=["mp4", "mov"], accept_multiple_files=True)
    story = st.text_area("Write your Urdu story here:", height=250)

if st.button("🚀 Create My Video"):
    if not v_files or not story:
        st.error("Please provide both video clips and a story.")
    elif ai_choice == "Gemini 3 Flash" and not gemini_k:
        st.error("Please enter Gemini Key in sidebar.")
    else:
        with st.status("Processing...") as status:
            # 1. Save uploads
            paths = []
            for i, f in enumerate(v_files):
                p = f"temp/c{i}.mp4"
                with open(p, "wb") as f_out: f_out.write(f.getbuffer())
                paths.append(p)
            
            # 2. Voiceover
            st.write("🎙️ Generating Male Urdu Voice...")
            v_path = "temp/voice.mp3"
            asyncio.run(generate_voiceover(story, v_path))
            
            # 3. Video Editing (Looping)
            st.write("🎬 Merging clips and matching to story length...")
            out_path = "temp/final_video.mp4"
            create_final_video(paths, v_path, out_path)
            
            # 4. AI Metadata
            st.write("🤖 Generating Title & Description...")
            meta = get_ai_metadata(story, ai_choice, gemini_k, grok_k)
            
            # 5. Thumbnail
            st.write("🖼️ Creating Thumbnail...")
            final_vid_obj = VideoFileClip(out_path)
            t_path = "temp/thumb.jpg"
            final_vid_obj.save_frame(t_path, t=1.0)
            
            status.update(label="Production Finished!", state="complete")

        st.divider()
        res1, res2 = st.columns(2)
        with res1:
            st.video(out_path)
            with open(out_path, "rb") as f:
                st.download_button("📥 Download Video", f, "urdu_video.mp4")
        
        with res2:
            st.image(t_path, caption="Auto-Generated Thumbnail")
            st.subheader("Metadata (Urdu)")
            st.write(meta)
