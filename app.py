import streamlit as st
import os
import tempfile
import time
import logging
from video_processor import VideoProcessor
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
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
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        color: #155724;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border: 1px solid #c3e6cb;
    }
    .info-box {
        padding: 1rem;
        background-color: #e3f2fd;
        color: #0c5460;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border: 1px solid #bee5eb;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        color: #721c24;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state"""
    if 'processor' not in st.session_state:
        st.session_state.processor = VideoProcessor()
    if 'temp_files' not in st.session_state:
        st.session_state.temp_files = []

def cleanup_temp_files():
    """Clean up temporary files"""
    for temp_file in st.session_state.temp_files:
        try:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        except:
            pass
    st.session_state.temp_files = []

def main():
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🎬 پیشہ ورانہ ویڈیو ایڈیٹنگ سسٹم</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">📌 ویڈیوز اپ لوڈ کریں، اردو اسکرپٹ لکھیں، اور مکمل ویڈیو بنائیں</div>', unsafe_allow_html=True)
    
    # Create two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 ویڈیو کلپس اپ لوڈ کریں")
        uploaded_videos = st.file_uploader(
            "ایک یا زیادہ ویڈیو کلپس منتخب کریں",
            type=['mp4', 'avi', 'mov', 'mkv'],
            accept_multiple_files=True
        )
        
        if uploaded_videos:
            st.success(f"✅ {len(uploaded_videos)} ویڈیو کلپس اپ لوڈ ہو گئے")
            
            # Show video details
            with st.expander("ویڈیوز کی تفصیلات"):
                for i, video in enumerate(uploaded_videos, 1):
                    size_mb = video.size / (1024 * 1024)
                    st.write(f"{i}. {video.name} ({size_mb:.2f} MB)")
    
    with col2:
        st.subheader("📝 ویڈیو اسکرپٹ لکھیں")
        script_text = st.text_area(
            "اردو میں اسکرپٹ لکھیں",
            placeholder="یہاں اپنی کہانی اردو میں لکھیں...",
            height=300
        )
        
        if script_text:
            word_count = len(script_text.split())
            st.info(f"📝 الفاظ کی تعداد: {word_count}")
            
            if word_count < 10:
                st.warning("⚠️ براہ کرم کم از کم 10 الفاظ لکھیں")
    
    # Process button
    process_button = st.button("🎬 ویڈیو بنائیں", type="primary", use_container_width=True)
    
    if process_button:
        # Validation
        if not uploaded_videos:
            st.error("❌ براہ کرم ویڈیوز اپ لوڈ کریں")
            return
            
        if not script_text or len(script_text.strip()) < 10:
            st.error("❌ براہ کرم کم از کم 10 الفاظ کا اسکرپٹ لکھیں")
            return
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Save videos
            status_text.info("📁 ویڈیوز محفوظ کی جا رہی ہیں...")
            video_paths = []
            
            for uploaded_video in uploaded_videos:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                    tmp_file.write(uploaded_video.read())
                    video_paths.append(tmp_file.name)
                    st.session_state.temp_files.append(tmp_file.name)
            
            progress_bar.progress(0.2)
            status_text.success(f"✅ {len(video_paths)} ویڈیوز محفوظ ہو گئیں")
            
            # Step 2: Generate voice
            status_text.info("🎤 اردو آواز تیار کی جا رہی ہے...")
            voice_path = os.path.join(st.session_state.processor.temp_dir, "voice.mp3")
            
            progress_bar.progress(0.3)
            voice_success = st.session_state.processor.generate_urdu_voice(script_text, voice_path)
            
            if voice_success:
                progress_bar.progress(0.4)
                status_text.success("✅ اردو آواز تیار ہو گئی")
            else:
                progress_bar.progress(0.4)
                status_text.warning("⚠️ آواز تیار نہیں ہو سکی، ویڈیو بغیر آواز کے بنے گی")
                voice_path = None
            
            # Step 3: Combine videos
            status_text.info("🎥 ویڈیوز کو ملایا جا رہا ہے (2-3 منٹ لگ سکتے ہیں)...")
            output_video_path = os.path.join(st.session_state.processor.temp_dir, "final_video.mp4")
            
            progress_bar.progress(0.5)
            
            # Show spinner during processing
            with st.spinner("پروسیسنگ جاری ہے... براہ کرم انتظار کریں"):
                combine_success = st.session_state.processor.combine_videos(
                    video_paths, 
                    output_video_path, 
                    voice_path
                )
            
            if combine_success:
                progress_bar.progress(0.7)
                status_text.success("✅ ویڈیوز کامیابی سے مل گئیں")
                
                # Step 4: Generate thumbnail
                status_text.info("🖼️ تھمب نیل تیار کیا جا رہا ہے...")
                thumbnail_path = os.path.join(st.session_state.processor.temp_dir, "thumbnail.jpg")
                title = st.session_state.processor.generate_title(script_text)
                
                progress_bar.progress(0.8)
                thumb_success = st.session_state.processor.generate_thumbnail(
                    output_video_path, 
                    thumbnail_path, 
                    title
                )
                
                if thumb_success:
                    progress_bar.progress(0.9)
                    status_text.success("✅ تھمب نیل تیار ہو گیا")
                else:
                    progress_bar.progress(0.9)
                    status_text.warning("⚠️ تھمب نیل تیار نہیں ہو سکا")
                    thumbnail_path = None
                
                # Get video duration
                duration = st.session_state.processor.get_video_duration(output_video_path)
                
                # Generate description
                description = st.session_state.processor.generate_description(
                    script_text, 
                    duration, 
                    len(video_paths)
                )
                
                progress_bar.progress(1.0)
                status_text.success("✅ ویڈیو کامیابی سے تیار ہو گئی!")
                
                # Display results
                st.markdown('<div class="success-message">🎉 مبارک ہو! آپ کی ویڈیو تیار ہے۔</div>', unsafe_allow_html=True)
                
                # Create tabs for results
                tab1, tab2, tab3 = st.tabs(["🎥 ویڈیو", "🖼️ تھمب نیل", "📝 معلومات"])
                
                with tab1:
                    st.subheader("تیار شدہ ویڈیو")
                    
                    # Read and display video
                    with open(output_video_path, 'rb') as f:
                        video_bytes = f.read()
                        st.video(video_bytes)
                    
                    # Download button
                    with open(output_video_path, 'rb') as f:
                        st.download_button(
                            label="📥 ویڈیو ڈاؤن لوڈ کریں",
                            data=f,
                            file_name=f"video_{int(time.time())}.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                
                with tab2:
                    if thumbnail_path and os.path.exists(thumbnail_path):
                        st.subheader("تھمب نیل")
                        
                        with open(thumbnail_path, 'rb') as f:
                            thumb_bytes = f.read()
                            st.image(thumb_bytes, use_container_width=True)
                        
                        with open(thumbnail_path, 'rb') as f:
                            st.download_button(
                                label="🖼️ تھمب نیل ڈاؤن لوڈ کریں",
                                data=f,
                                file_name=f"thumbnail_{int(time.time())}.jpg",
                                mime="image/jpeg",
                                use_container_width=True
                            )
                    else:
                        st.warning("تھمب نیل دستیاب نہیں ہے")
                
                with tab3:
                    st.subheader("📌 ویڈیو ٹائٹل")
                    st.markdown(f"### {title}")
                    
                    st.subheader("📝 ویڈیو تفصیل")
                    st.markdown(description)
                    
                    st.download_button(
                        label="📄 تفصیل ڈاؤن لوڈ کریں",
                        data=description,
                        file_name=f"description_{int(time.time())}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                # Show success animation
                st.balloons()
                
            else:
                st.markdown('<div class="error-box">❌ ویڈیوز کو ملانے میں خرابی ہوئی۔ براہ کرم دوبارہ کوشش کریں</div>', unsafe_allow_html=True)
                st.info("💡 تجاویز:\n- ویڈیوز کا فارمیٹ MP4 ہو\n- ویڈیوز کا سائز کم کریں\n- کم ویڈیوز کے ساتھ آزمائیں")
                
        except Exception as e:
            logger.error(f"Error: {traceback.format_exc()}")
            st.markdown(f'<div class="error-box">❌ خرابی: {str(e)}</div>', unsafe_allow_html=True)
            st.info("براہ کرم دوبارہ کوشش کریں")
        
        finally:
            # Clean up temporary files
            cleanup_temp_files()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📋 معلومات")
        st.markdown("""
        ### استعمال کرنے کا طریقہ:
        1. **ویڈیوز اپ لوڈ کریں** - کم از کم 1 ویڈیو
        2. **اسکرپٹ لکھیں** - اردو میں
        3. **ویڈیو بنائیں** - بٹن دبائیں
        
        ### خصوصیات:
        - ✅ اردو آواز
        - ✅ ویڈیوز ملانا
        - ✅ تھمب نیل بنانا
        - ✅ ٹائٹل اور تفصیل
        
        ### سپورٹڈ فارمیٹس:
        - MP4, AVI, MOV, MKV
        - زیادہ سے زیادہ 10 ویڈیوز
        - ہر ویڈیو 200MB تک
        """)
        
        st.markdown("---")
        st.markdown("**🎬 ورژن:** 2.0")
        
        # Clear cache button
        if st.button("🗑️ کیش صاف کریں"):
            cleanup_temp_files()
            st.session_state.processor.cleanup_temp_files()
            st.success("کیش صاف ہو گیا")

if __name__ == "__main__":
    main()
