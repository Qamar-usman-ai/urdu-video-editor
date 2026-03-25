import streamlit as st
import os
import tempfile
import json
from pathlib import Path
from datetime import datetime
import subprocess
import cv2
import numpy as np

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
if 'uploaded_videos' not in st.session_state:
    st.session_state.uploaded_videos = None
if 'script_input' not in st.session_state:
    st.session_state.script_input = ""
if 'video_title' not in st.session_state:
    st.session_state.video_title = ""
if 'video_description' not in st.session_state:
    st.session_state.video_description = ""
if 'voice_speed' not in st.session_state:
    st.session_state.voice_speed = 1.0
if 'video_quality' not in st.session_state:
    st.session_state.video_quality = "720p"
if 'video_category' not in st.session_state:
    st.session_state.video_category = "علوم و تعلیم"

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
        type=["mp4", "avi", "mov", "mkv", "flv", "mpeg4"],
        accept_multiple_files=True,
        key="video_uploader"
    )
    
    if uploaded_videos:
        st.session_state.uploaded_videos = uploaded_videos
        st.success(f"✅ {len(uploaded_videos)} video(s) uploaded")
        
        # Show warning if less than 5 videos
        if len(uploaded_videos) < 5:
            st.warning(f"⚠️ You have {len(uploaded_videos)} clip(s). Recommended: 5 or more")
        
        with st.expander("📊 Video Details"):
            for i, video in enumerate(uploaded_videos):
                st.write(f"**Video {i+1}:** {video.name} ({video.size / (1024*1024):.2f} MB)")
    else:
        st.info("📂 No videos uploaded yet")

with col2:
    st.subheader("📝 Script/Story")
    st.markdown("Write your story in Urdu")
    
    default_script = """یہ کہانی ہے علی کی۔ ایک عام سے مگر خواب دیکھنے والے لڑکے کی۔ اس کی آنکھوں میں ایک خواب تھا، پاکستان کا CSS آفیسر بننے کا خواب۔

اس نے کوشش کی، رات دن ایک کر دیا۔ لیکن ناکامی، ہر بار ناکامی۔ پہلی بار، دوسری بار، تیسری بار۔ ہر بار وہ گرتا گیا۔

ناکامی نے اس کے اندر کی روشنی بجھا دی۔ وہ تنہا ہوتا چلا گیا، ڈپریشن اس کا مقدر بن گیا۔

آخر اس دن اس نے سب کچھ ختم کرنے کا فیصلہ کر لیا۔ وہ اپنی زندگی کی سب سے بڑی غلطی کرنے ہی والا تھا کہ... ایک ہاتھ نے اس کا کندھا تھاما۔

یہ بزرگ کوئی اور نہیں، ایک اللہ والا تھا۔ اس نے علی کو سمجھایا، اللہ نے تجھے اس لیے بنایا ہے کہ تو کچھ بنے۔

علی نے اپنی سوچ بدل دی۔ اس نے محنت کو اپنا راستہ اور اللہ پر بھروسے کو اپنی طاقت بنا لیا۔

وہ دن آیا۔ علی، وہی لڑکا جو ہار مان چکا تھا، آج پاکستان کا CSS آفیسر تھا۔"""
    
    script_input = st.text_area(
        "Enter your Urdu script",
        height=250,
        value=st.session_state.script_input if st.session_state.script_input else default_script,
        placeholder="یہاں اپنی اردو کہانی لکھیں...\n\nExample: میرا نام علی ہے۔ میں ایک فلم بنا رہا ہوں...",
        key="script_input_area"
    )
    st.session_state.script_input = script_input
    
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
        value=st.session_state.voice_speed,
        step=0.1,
        help="1.0 = Normal, <1.0 = Slower, >1.0 = Faster",
        key="voice_speed_slider"
    )
    st.session_state.voice_speed = voice_speed

with config_col2:
    video_quality = st.selectbox(
        "Video Quality",
        ["360p", "480p", "720p", "1080p"],
        index=2,
        help="Higher quality = larger file size",
        key="video_quality_select"
    )
    st.session_state.video_quality = video_quality

with config_col3:
    background_music = st.checkbox(
        "Add Background Music",
        value=False,
        help="Optional background music",
        key="bg_music_checkbox"
    )

st.divider()

# Video metadata
st.subheader("📋 Video Metadata")

meta_col1, meta_col2 = st.columns(2)

with meta_col1:
    video_title = st.text_input(
        "Video Title (Urdu/English)",
        value=st.session_state.video_title if st.session_state.video_title else "ناکامی سے ڈپریشن، خودکشی کی کوشش سے CSS آفیسر تک: ایک کہانی",
        placeholder="مثال: میرا پہلا ویڈیو",
        key="title_input"
    )
    st.session_state.video_title = video_title
    
    video_category = st.selectbox(
        "Category",
        ["علوم و تعلیم", "تفریح", "خبریں", "ٹیکنالوجی", "دوسرہ"],
        index=0,
        key="category_select"
    )
    st.session_state.video_category = video_category

with meta_col2:
    default_description = """یہ ویڈیو ایک نوجوان کی متاثر کن حقیقی کہانی ہے جو ہر بار ناکام ہوا، ڈپریشن کا شکار ہوا، اور خودکشی کی کوشش تک جا پہنچا۔ لیکن ایک "اللہ والے" بزرگ کی مدد نے اس کی زندگی بدل دی۔

یہ کہانی ہر اس شخص کے لیے ہے جو ناکامی سے مایوس ہے، جو زندگی سے ہار چکا ہے، جو ڈپریشن میں مبتلا ہے۔ یاد رکھیں، ہر ناکامی کامیابی کا ایک قدم ہے۔ بس ہمت نہ ہاریں، محنت جاری رکھیں، اور اللہ پر بھروسہ کریں۔"""
    
    video_description = st.text_area(
        "Video Description (Urdu/English)",
        value=st.session_state.video_description if st.session_state.video_description else default_description,
        height=100,
        placeholder="اپنی ویڈیو کی تفصیل لکھیں...",
        key="description_input"
    )
    st.session_state.video_description = video_description

st.divider()

# Process button
if st.button("🚀 Start Processing", use_container_width=True, type="primary"):
    # Validation
    if not st.session_state.uploaded_videos:
        st.error("❌ Please upload at least one video clip")
    elif not st.session_state.script_input:
        st.error("❌ Please enter your script")
    elif not st.session_state.video_title:
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
            for i, video_file in enumerate(st.session_state.uploaded_videos):
                video_path = os.path.join(temp_dir, f"clip_{i}_{video_file.name}")
                with open(video_path, "wb") as f:
                    f.write(video_file.read())
                video_paths.append(video_path)
            
            # Import processors
            from video_processor import VideoProcessor
            from voice_generator import VoiceGenerator
            from metadata_generator import MetadataGenerator
            
            # Initialize processors
            video_processor = VideoProcessor()
            voice_generator = VoiceGenerator()
            metadata_gen = MetadataGenerator()
            
            # Step 1: Combine videos
            status_text.info("🎬 Combining video clips...")
            progress_bar.progress(25)
            
            # Get resolution from quality setting
            resolution_map = {
                "360p": (480, 360),
                "480p": (854, 480),
                "720p": (1280, 720),
                "1080p": (1920, 1080)
            }
            resolution = resolution_map.get(st.session_state.video_quality, (1280, 720))
            
            combined_video = os.path.join(output_dir, "combined.mp4")
            combined_success = video_processor.combine_videos(video_paths, combined_video, resolution)
            
            if not combined_success:
                raise Exception("Failed to combine videos")
            
            # Step 2: Generate voice
            status_text.info("🎙️ Generating Urdu voice-over...")
            progress_bar.progress(50)
            
            audio_file = os.path.join(output_dir, "voiceover.wav")
            voice_success = voice_generator.generate_voice(
                st.session_state.script_input, 
                audio_file, 
                st.session_state.voice_speed
            )
            
            if not voice_success:
                raise Exception("Failed to generate voice-over")
            
            # Step 3: Sync audio with video
            status_text.info("🔊 Syncing audio with video...")
            progress_bar.progress(75)
            
            final_video = os.path.join(output_dir, "final_video.mp4")
            audio_success = video_processor.add_audio_to_video(combined_video, audio_file, final_video)
            
            if not audio_success:
                # Fallback: just copy combined video
                import shutil
                shutil.copy(combined_video, final_video)
            
            # Step 4: Generate thumbnail
            status_text.info("🖼️ Generating thumbnail...")
            progress_bar.progress(85)
            
            thumbnail = os.path.join(output_dir, "thumbnail.jpg")
            thumbnail_success = video_processor.generate_thumbnail(final_video, thumbnail)
            
            if not thumbnail_success:
                # Create a simple fallback thumbnail
                import numpy as np
                img = np.zeros((720, 1280, 3), dtype=np.uint8)
                cv2.putText(img, "Video Thumbnail", (100, 360), 
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
                cv2.imwrite(thumbnail, img)
            
            # Step 5: Generate metadata
            status_text.info("📝 Generating metadata...")
            progress_bar.progress(95)
            
            video_duration = video_processor.get_video_duration(final_video)
            
            metadata = metadata_gen.generate_metadata(
                title=st.session_state.video_title,
                description=st.session_state.video_description,
                category=st.session_state.video_category,
                video_duration=video_duration,
                script=st.session_state.script_input,
                voice_speed=st.session_state.voice_speed,
                video_quality=st.session_state.video_quality
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
                "temp_dir": temp_dir,
                "video_paths": video_paths,
                "audio_file": audio_file
            }
            
        except Exception as e:
            st.error(f"❌ Error during processing: {str(e)}")
            st.exception(e)  # Show full exception for debugging
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
        if os.path.exists(output["video"]):
            st.video(output["video"])
        else:
            st.error("Video file not found")
    
    with col2:
        st.markdown("### 🖼️ Thumbnail")
        if os.path.exists(output["thumbnail"]):
            st.image(output["thumbnail"], use_container_width=True)
        else:
            st.warning("Thumbnail not available")
        
        st.markdown("### 📋 Video Info")
        metadata = output["metadata"]
        
        # Display metadata nicely
        st.json({
            "Title": metadata.get("title", "N/A"),
            "Category": metadata.get("category", "N/A"),
            "Duration": metadata.get("duration", "N/A"),
            "Created": metadata.get("created_at", "N/A"),
            "Voice Speed": metadata.get("voice_speed", "N/A"),
            "Quality": metadata.get("video_quality", "N/A")
        })
    
    st.divider()
    
    # Download section
    st.subheader("📥 Download Files")
    
    download_col1, download_col2, download_col3 = st.columns(3)
    
    with download_col1:
        if os.path.exists(output["video"]):
            with open(output["video"], "rb") as f:
                st.download_button(
                    label="📹 Download Video",
                    data=f.read(),
                    file_name=f"{st.session_state.video_title.replace(' ', '_')}.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )
    
    with download_col2:
        if os.path.exists(output["thumbnail"]):
            with open(output["thumbnail"], "rb") as f:
                st.download_button(
                    label="🖼️ Download Thumbnail",
                    data=f.read(),
                    file_name="thumbnail.jpg",
                    mime="image/jpeg",
                    use_container_width=True
                )
    
    with download_col3:
        if os.path.exists(output["metadata_file"]):
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
        # Clean up temp files
        import shutil
        if os.path.exists(output["temp_dir"]):
            shutil.rmtree(output["temp_dir"], ignore_errors=True)
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
