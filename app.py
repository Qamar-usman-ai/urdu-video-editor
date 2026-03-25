import streamlit as st
import os
import asyncio
import edge_tts
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, vfx
import google.generativeai as genai
from openai import OpenAI

# --- Directory Setup ---
TEMP_DIR = "temp_assets"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# --- Logic Functions ---

def get_metadata_ai(script, provider, gemini_key, grok_key):
    """Generates Title and Description using chosen AI."""
    prompt = f"Based on this Urdu script: '{script}', write a catchy Video Title and a YouTube-style description in Urdu. Use simple, human-like words."
    try:
        if provider == "Gemini 3 Flash":
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            return model.generate_content(prompt).text
        elif provider == "Grok (xAI)":
            client = OpenAI(api_key=grok_key, base_url="https://api.x.ai/v1")
            response = client.chat.completions.create(
                model="grok-beta",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
    except Exception as e:
        return f"Metadata Error: {str(e)}"

async def create_voiceover(text, output_path):
    """Generates a professional Male Urdu voice (Asad)."""
    # 'ur-PK-AsadNeural' is the standard high-quality Pakistani Male voice
    communicate = edge_tts.Communicate(text, "ur-PK-AsadNeural")
    await communicate.save(output_path)

def process_and_sync_video(video_paths, voice_path, final_out_path):
    """Combines clips and slows them down to match the voiceover perfectly."""
    audio = AudioFileClip(voice_path)
    target_duration = audio.duration
    
    # Load all clips
    clips = [VideoFileClip(v) for v in video_paths]
    
    # Calculate original total length
    original_total_duration = sum(c.duration for c in clips)
    
    # Calculate speed factor (e.g., 0.5 means half speed/slower)
    speed_factor = original_total_duration / target_duration
    
    # Apply speed change to each clip to 'stretch' it
    stretched_clips = [c.fx(vfx.speedx, speed_factor) for c in clips]
    
    # Merge them
    final_video = concatenate_videoclips(stretched_clips, method="compose")
    
    # Ensure exact sync and add audio
    final_video = final_video.set_duration(target_duration).set_audio(audio)
    
    # Export with standard settings
    final_video.write_videofile(
        final_out_path, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac",
        temp_audiofile='temp-audio.m4a', 
        remove_temp=True
    )
    
    # Close resources
    for c in clips: c.close()
    final_video.close()

# --- Streamlit UI ---

st.set_page_config(page_title="Urdu Story Studio", page_icon="🎬", layout="wide")

st.title("🎙️ Urdu Story Studio")
st.markdown("##### Upload clips and a script to create a perfectly synced Urdu video with a Male voice.")

# Sidebar for API Keys
with st.sidebar:
    st.header("🔑 API Keys")
    ai_choice = st.selectbox("Choose AI Model", ["Gemini 3 Flash", "Grok (xAI)"])
    gem_key = st.text_input("Gemini API Key", type="password")
    gro_key = st.text_input("Grok API Key", type="password")
    st.info("The video clips will be slowed down automatically to match your script length.")

# Main Inputs
c1, c2 = st.columns(2)

with c1:
    uploaded_clips = st.file_uploader("Upload 5-6 Video Clips", type=["mp4", "mov"], accept_multiple_files=True)
    
with c2:
    # Example script provided for your Ali story
    example_script = """السلام علیکم۔ یہ کہانی ہے علی کی۔ ایک عام سے مگر خواب دیکھنے والے لڑکے کی۔
چھوٹے سے شہر میں پیدا ہونے والا یہ لڑکا جب بھی آسمان کی طرف دیکھتا، اس کی آنکھوں میں ایک خواب چمکتا تھا۔
ایک خواب جو کہنے والوں کو ہنسی آتی تھی۔ وہ خواب تھا... پاکستان کا CSS آفیسر بننا۔
اپنے والدین کا نام روشن کرنا۔ اس ملک کی خدمت کرنا۔
یہ خواب اس کے دل میں اتنا گہرا تھا کہ وہ رات دن اس کی تعبیر کی تلاش میں رہتا۔"""
    user_script = st.text_area("Paste your Complete Story Script:", value=example_script, height=250)

if st.button("🚀 Generate Final Video"):
    if not uploaded_clips or not user_script:
        st.error("Please provide both video clips and a script.")
    elif ai_choice == "Gemini 3 Flash" and not gem_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    else:
        with st.status("Building your video story...") as status:
            # 1. Save local copies of clips
            clip_paths = []
            for i, clip in enumerate(uploaded_clips):
                temp_p = os.path.join(TEMP_DIR, f"raw_{i}.mp4")
                with open(temp_p, "wb") as f:
                    f.write(clip.getbuffer())
                clip_paths.append(temp_p)
            
            # 2. Generate Voiceover
            st.write("🎙️ Generating Male Urdu Voice (Asad)...")
            voice_file = os.path.join(TEMP_DIR, "voiceover.mp3")
            asyncio.run(create_voiceover(user_script, voice_file))
            
            # 3. Video Processing (Stretching/Slowing)
            st.write("🎬 Stretching video to match story length...")
            output_file = os.path.join(TEMP_DIR, "final_story_video.mp4")
            process_and_sync_video(clip_paths, voice_file, output_file)
            
            # 4. Metadata Generation
            st.write("🤖 Generating AI Metadata...")
            meta_data = get_metadata_ai(user_script, ai_choice, gem_key, gro_key)
            
            # 5. Thumbnail Generation
            st.write("🖼️ Capturing Thumbnail...")
            final_clip_obj = VideoFileClip(output_file)
            thumb_file = os.path.join(TEMP_DIR, "thumbnail.jpg")
            final_clip_obj.save_frame(thumb_file, t=1.0)
            
            status.update(label="Video Production Complete!", state="complete")

        st.divider()
        
        # Display Results
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.video(output_file)
            with open(output_file, "rb") as f:
                st.download_button("📥 Download Video", f, "urdu_story.mp4")
        
        with res_col2:
            st.image(thumb_file, caption="Auto-Generated Thumbnail")
            st.subheader("Title & Description (Urdu)")
            st.write(meta_data)
