import streamlit as st
import os
import tempfile
import json
from pathlib import Path
from datetime import datetime
import subprocess

from video_processor import VideoProcessor
from voice_generator import VoiceGenerator
from metadata_generator import MetadataGenerator

# Page configuration
st.set_page_config(
    page_title="Urdu Video Editor Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    .stProgress > div > div > div > div {
        background-color: #FF6B6B;
    }
    .success-box {
        background-color: #D4EDDA;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #C3E6CB;
        margin: 10px 0;
    }
    .info-box {
        background-color: #D1ECF1;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #BEE5EB;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'output_data' not in st.session_state:
    st.session_state.output_data = None

# Main title
st.title("🎬 Urdu Video Editor Pro")
st.markdown("*Create professional videos with Urdu voice-over*")

# Sidebar
with st.sidebar:
    st.header("📋 Guide")
    st.markdown("""
    ### How to use:
    1. **Upload Video Clips** - Add 5+ clips (MP4, AVI, MOV)
    2. **Write Your Script** - Enter Urdu story/script
    3. **Configure Settings** - Choose voice speed, quality
    4. **Process** - System will combine clips + add audio
    5. **Download** - Get final video, thumbnail, metadata
    
    ### Requirements:
    - Each clip: 5+ seconds
    - Video format: MP4, AVI, MOV
    - Audio: Auto-generated in Urdu
    - Resolution: 1080p recommended
    """)
    
    st.divider()
    st.markdown("**Made for Pakistani creators** 🇵🇰")

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("📹 Video Clips")
    st.markdown("Upload your video clips (5 or more)")
    
    uploaded_videos = st.file_uploader(
        "Choose video files",
        type=["mp4", "avi", "mov", "mkv", "flv"],
        accept_multiple_files=True,
        key="video_uploader"
    )
    
    if uploaded_videos:
        st.success(f"✅ {len(uploaded_videos)} video(s) uploaded")
        with st.expander("📊 Video Details"):
            for i, video in enumerate(uploaded_videos):
                st.write(f"**Video {i+1}:** {video.name} ({video.size / (1024*1024):.2f} MB)")

with col2:
    st.subheader("📝 Script/Story")
    st.markdown("Write your story in Urdu")
    
    script_input = st.text_area(
        "Enter your Urdu script",
        height=250,
        placeholder="یہاں اپنی اردو کہانی لکھیں...\n\nExample: میرا نام علی ہے۔ میں ایک فلم بنا رہا ہوں...",
        key="script_input"
    )
    
    if script_input:
        word_count = len(script_input.split())
        st.caption(f"📄 Words: {word_count}")

st.divider()

# Configuration section
st.subheader("⚙️ Configuration Settings")

config_col1, config_col2, config_col3 = st.columns(3)

with config_col1:
    voice_speed = st.slider(
        "Voice Speed",
        min_value=0.5,
        max_value=2.0,
        value=1.0,
        step=0.1,
        help="1.0 = Normal, <1.0 = Slower, >1.0 = Faster"
    )

with config_col2:
    video_quality = st.selectbox(
        "Video Quality",
        ["360p", "480p", "720p", "1080p"],
        index=2,
        help="Higher quality = larger file size"
    )

with config_col3:
    background_music = st.checkbox(
        "Add Background Music",
        value=False,
        help="Optional background music"
    )

st.divider()

# Video metadata
st.subheader("📋 Video Metadata")

meta_col1, meta_col2 = st.columns(2)

with meta_col1:
    video_title = st.text_input(
        "Video Title (Urdu/English)",
        placeholder="مثال: میرا پہلا ویڈیو",
        key="title_input"
    )
    
    video_category = st.selectbox(
        "Category",
        ["علوم و تعلیم", "تفریح", "خبریں", "ٹیکنالوجی", "دوسرہ"],
        key="category_select"
    )

with meta_col2:
    video_description = st.text_area(
        "Video Description (Urdu/English)",
        height=100,
        placeholder="اپنی ویڈیو کی تفصیل لکھیں...",
        key="description_input"
    )

st.divider()

# Process button
if st.button("🚀 Start Processing", use_container_width=True, type="primary"):
    # Validation
    if not uploaded_videos:
        st.error("❌ Please upload at least one video clip")
    elif len(uploaded_videos) < 5:
        st.warning(f"⚠️ You have {len(uploaded_videos)} clip(s). Recommended: 5 or more")
    elif not script_input:
        st.error("❌ Please enter your script")
    elif not video_title:
        st.error("❌ Please enter a video title")
    else:
        st.session_state.processing = True
        
        # Create progress container
        progress_container = st.container()
        status_container = st.container()
        
        try:
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(output_dir, exist_ok=True)
            
            # Save uploaded videos
            status_text.info("💾 Saving video clips...")
            progress_bar.progress(10)
            
            video_paths = []
            for i, video_file in enumerate(uploaded_videos):
                video_path = os.path.join(temp_dir, f"clip_{i}.mp4")
                with open(video_path, "wb") as f:
                    f.write(video_file.read())
                video_paths.append(video_path)
            
            # Initialize processors
            video_processor = VideoProcessor()
            voice_generator = VoiceGenerator()
            metadata_gen = MetadataGenerator()
            
            # Step 1: Combine videos
            status_text.info("🎬 Combining video clips...")
            progress_bar.progress(25)
            
            combined_video = os.path.join(output_dir, "combined.mp4")
            video_processor.combine_videos(video_paths, combined_video, video_quality)
            
            # Step 2: Generate voice
            status_text.info("🎙️ Generating Urdu voice-over...")
            progress_bar.progress(50)
            
            audio_file = os.path.join(output_dir, "voiceover.wav")
            voice_generator.generate_voice(script_input, audio_file, voice_speed)
            
            # Step 3: Sync audio with video
            status_text.info("🔊 Syncing audio with video...")
            progress_bar.progress(75)
            
            final_video = os.path.join(output_dir, "final_video.mp4")
            video_processor.add_audio_to_video(combined_video, audio_file, final_video)
            
            # Step 4: Generate thumbnail
            status_text.info("🖼️ Generating thumbnail...")
            progress_bar.progress(85)
            
            thumbnail = os.path.join(output_dir, "thumbnail.jpg")
            video_processor.generate_thumbnail(final_video, thumbnail)
            
            # Step 5: Generate metadata
            status_text.info("📝 Generating metadata...")
            progress_bar.progress(95)
            
            metadata = metadata_gen.generate_metadata(
                title=video_title,
                description=video_description,
                category=video_category,
                video_duration=video_processor.get_video_duration(final_video),
                script=script_input
            )
            
            metadata_file = os.path.join(output_dir, "metadata.json")
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            progress_bar.progress(100)
            status_text.success("✅ Processing completed successfully!")
            
            # Store output data
            st.session_state.output_data = {
                "video": final_video,
                "thumbnail": thumbnail,
                "metadata": metadata,
                "metadata_file": metadata_file,
                "temp_dir": temp_dir
            }
            
        except Exception as e:
            st.error(f"❌ Error during processing: {str(e)}")
            st.write("Debug info:", e)
        finally:
            st.session_state.processing = False

st.divider()

# Results section
if st.session_state.output_data:
    st.subheader("✅ Processing Complete!")
    
    output = st.session_state.output_data
    
    # Display preview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎥 Video Preview")
        st.video(output["video"])
    
    with col2:
        st.markdown("### 🖼️ Thumbnail")
        st.image(output["thumbnail"], use_column_width=True)
        
        st.markdown("### 📋 Video Info")
        metadata = output["metadata"]
        st.json({
            "Title": metadata.get("title"),
            "Category": metadata.get("category"),
            "Duration": metadata.get("duration"),
            "Created": metadata.get("created_at"),
            "Description": metadata.get("description")
        })
    
    st.divider()
    
    # Download section
    st.subheader("📥 Download Files")
    
    download_col1, download_col2, download_col3 = st.columns(3)
    
    with download_col1:
        with open(output["video"], "rb") as f:
            st.download_button(
                label="📹 Download Video",
                data=f.read(),
                file_name="final_video.mp4",
                mime="video/mp4",
                use_container_width=True
            )
    
    with download_col2:
        with open(output["thumbnail"], "rb") as f:
            st.download_button(
                label="🖼️ Download Thumbnail",
                data=f.read(),
                file_name="thumbnail.jpg",
                mime="image/jpeg",
                use_container_width=True
            )
    
    with download_col3:
        with open(output["metadata_file"], "rb") as f:
            st.download_button(
                label="📋 Download Metadata",
                data=f.read(),
                file_name="metadata.json",
                mime="application/json",
                use_container_width=True
            )
    
    st.divider()
    
    # Clear session button
    if st.button("🔄 Process Another Video", use_container_width=True):
        st.session_state.output_data = None
        st.rerun()

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.9em; margin-top: 30px;'>
        <p>🇵🇰 Urdu Video Editor Pro v1.0</p>
        <p>Developed for Pakistani content creators</p>
    </div>
    """, unsafe_allow_html=True)
