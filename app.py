import streamlit as st
import os
import tempfile
import time
import logging
from video_processor import VideoProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Urdu Video Editor",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        color: #ff4b4b;
        text-align: center;
        padding: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #e3f2fd;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session
if 'processor' not in st.session_state:
    st.session_state.processor = VideoProcessor()
if 'temp_files' not in st.session_state:
    st.session_state.temp_files = []

def cleanup():
    """Clean temp files"""
    for f in st.session_state.temp_files:
        try:
            if os.path.exists(f):
                os.unlink(f)
        except:
            pass
    st.session_state.temp_files = []

def main():
    # Header
    st.markdown('<div class="main-header">🎬 Urdu Video Editor</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">📌 Upload videos, write Urdu script, and create a complete video</div>', 
                unsafe_allow_html=True)
    
    # Two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Upload Videos")
        uploaded_files = st.file_uploader(
            "Select video clips (MP4 format recommended)",
            type=['mp4', 'MP4'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} videos uploaded")
            for i, f in enumerate(uploaded_files[:5], 1):
                size = f.size / (1024 * 1024)
                st.write(f"{i}. {f.name} ({size:.1f} MB)")
    
    with col2:
        st.subheader("📝 Write Urdu Script")
        script = st.text_area(
            "Enter your Urdu script/story",
            height=250,
            placeholder="السلام علیکم۔ یہ کہانی ہے علی کی..."
        )
        
        if script:
            word_count = len(script.split())
            st.info(f"📝 Word count: {word_count}")
            if word_count < 20:
                st.warning("⚠️ Please write at least 20 words")
    
    # Process button
    if st.button("🎬 Create Video", type="primary", use_container_width=True):
        if not uploaded_files:
            st.error("❌ Please upload at least one video")
            return
            
        if not script or len(script.strip()) < 20:
            st.error("❌ Please write a script with at least 20 words")
            return
        
        # Progress tracking
        progress = st.progress(0)
        status = st.empty()
        
        try:
            # Step 1: Save videos
            status.info("📁 Saving videos...")
            video_paths = []
            
            for uploaded in uploaded_files:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
                    tmp.write(uploaded.read())
                    video_paths.append(tmp.name)
                    st.session_state.temp_files.append(tmp.name)
            
            progress.progress(20)
            status.success(f"✅ {len(video_paths)} videos saved")
            
            # Step 2: Generate voice
            status.info("🎤 Generating Urdu voice...")
            voice_path = os.path.join(st.session_state.processor.temp_dir, "voice.mp3")
            
            progress.progress(30)
            voice_success = st.session_state.processor.generate_urdu_voice(script, voice_path)
            
            if voice_success:
                progress.progress(40)
                status.success("✅ Voice generated")
            else:
                progress.progress(40)
                status.warning("⚠️ Voice generation failed, video will be silent")
                voice_path = None
            
            # Step 3: Combine videos
            status.info("🎥 Combining videos (this may take 2-3 minutes)...")
            output_path = os.path.join(st.session_state.processor.temp_dir, "output.mp4")
            
            progress.progress(50)
            
            # Show spinner while processing
            with st.spinner("Processing videos... Please wait"):
                success = st.session_state.processor.combine_videos(
                    video_paths, 
                    output_path, 
                    voice_path
                )
            
            if success:
                progress.progress(80)
                status.success("✅ Videos combined successfully")
                
                # Step 4: Generate thumbnail
                status.info("🖼️ Generating thumbnail...")
                thumb_path = os.path.join(st.session_state.processor.temp_dir, "thumb.jpg")
                title = st.session_state.processor.generate_title(script)
                
                thumb_success = st.session_state.processor.generate_thumbnail(
                    output_path, 
                    thumb_path, 
                    title
                )
                
                progress.progress(90)
                if thumb_success:
                    status.success("✅ Thumbnail generated")
                else:
                    status.warning("⚠️ Thumbnail generation failed")
                
                # Get duration
                duration = st.session_state.processor.get_video_duration(output_path)
                
                # Generate description
                description = st.session_state.processor.generate_description(
                    script, 
                    duration, 
                    len(video_paths)
                )
                
                progress.progress(100)
                status.success("✅ Video created successfully!")
                
                # Show results
                st.markdown('<div class="success-box">🎉 Congratulations! Your video is ready.</div>', 
                           unsafe_allow_html=True)
                
                # Tabs for results
                tab1, tab2, tab3 = st.tabs(["🎥 Video", "🖼️ Thumbnail", "📝 Details"])
                
                with tab1:
                    st.subheader("Final Video")
                    
                    # Read and display video
                    with open(output_path, 'rb') as f:
                        video_data = f.read()
                        st.video(video_data)
                    
                    # Download button
                    with open(output_path, 'rb') as f:
                        st.download_button(
                            label="📥 Download Video",
                            data=f,
                            file_name=f"video_{int(time.time())}.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                
                with tab2:
                    if thumb_success and os.path.exists(thumb_path):
                        st.subheader("Video Thumbnail")
                        with open(thumb_path, 'rb') as f:
                            thumb_data = f.read()
                            st.image(thumb_data, use_container_width=True)
                        
                        with open(thumb_path, 'rb') as f:
                            st.download_button(
                                label="🖼️ Download Thumbnail",
                                data=f,
                                file_name=f"thumb_{int(time.time())}.jpg",
                                mime="image/jpeg",
                                use_container_width=True
                            )
                    else:
                        st.warning("Thumbnail not available")
                
                with tab3:
                    st.subheader("📌 Video Title")
                    st.markdown(f"### {title}")
                    
                    st.subheader("📝 Description")
                    st.markdown(description)
                    
                    st.download_button(
                        label="📄 Download Description",
                        data=description,
                        file_name=f"description_{int(time.time())}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                # Celebration
                st.balloons()
                
            else:
                st.markdown('<div class="error-box">❌ Failed to combine videos. Please check the videos and try again.</div>', 
                           unsafe_allow_html=True)
                st.info("💡 Tips:\n- Use MP4 format videos\n- Keep videos under 100MB\n- Try with 1-2 videos first")
                
        except Exception as e:
            logger.error(f"Error: {e}")
            st.markdown(f'<div class="error-box">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
            st.info("Please check the console for details")
        
        finally:
            # Clean up
            cleanup()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📋 Instructions")
        st.markdown("""
        ### How to use:
        1. **Upload videos** - MP4 format recommended
        2. **Write script** - Urdu language
        3. **Create video** - Click the button
        
        ### Features:
        - ✅ Urdu voiceover
        - ✅ Combine videos
        - ✅ Generate thumbnail
        - ✅ Auto title & description
        
        ### Requirements:
        - Python 3.8+
        - FFmpeg installed
        - Internet for voice
        
        ### Tips:
        - Start with 1-2 small videos
        - Use MP4 format
        - Script should be 20+ words
        """)
        
        st.markdown("---")
        st.markdown("**Version:** 2.0")
        
        if st.button("🗑️ Clear Cache"):
            cleanup()
            st.session_state.processor.cleanup()
            st.success("Cache cleared")

if __name__ == "__main__":
    main()
