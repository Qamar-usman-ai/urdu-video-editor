import streamlit as st
import os
import tempfile
from pathlib import Path
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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #ff4b4b;
        text-align: center;
        margin-bottom: 2rem;
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
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        color: #856404;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border: 1px solid #ffeaa7;
    }
    .stButton > button {
        width: 100%;
        font-size: 1.2rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'video_processor' not in st.session_state:
        st.session_state.video_processor = VideoProcessor()
    if 'videos_processed' not in st.session_state:
        st.session_state.videos_processed = False
    if 'temp_files' not in st.session_state:
        st.session_state.temp_files = []

def cleanup_temp_files():
    """Clean up temporary files"""
    for temp_file in st.session_state.get('temp_files', []):
        try:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        except:
            pass
    st.session_state.temp_files = []

def main():
    initialize_session_state()
    
    st.markdown('<div class="main-header">🎬 پیشہ ورانہ ویڈیو ایڈیٹنگ سسٹم</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="info-box">📌 اس سسٹم میں آپ اپنی ویڈیوز اپ لوڈ کریں، اردو اسکرپٹ لکھیں، اور مکمل ویڈیو بنائیں۔</div>', unsafe_allow_html=True)
    
    # Create columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 ویڈیو کلپس اپ لوڈ کریں")
        uploaded_videos = st.file_uploader(
            "ایک یا زیادہ ویڈیو کلپس منتخب کریں (MP4, AVI, MOV, MKV)",
            type=['mp4', 'avi', 'mov', 'mkv', 'MP4', 'AVI', 'MOV', 'MKV'],
            accept_multiple_files=True
        )
        
        if uploaded_videos:
            if len(uploaded_videos) >= 5:
                st.success(f"✅ {len(uploaded_videos)} ویڈیو کلپس اپ لوڈ ہو گئے")
            else:
                st.info(f"📹 {len(uploaded_videos)} ویڈیو کلپس اپ لوڈ ہو گئے۔ مزید بھی شامل کر سکتے ہیں۔")
            
            # Display video previews
            with st.expander("ویڈیوز کی تفصیلات دیکھیں"):
                for i, video in enumerate(uploaded_videos, 1):
                    st.write(f"{i}. {video.name} - {video.size / 1024 / 1024:.2f} MB")
    
    with col2:
        st.subheader("📝 ویڈیو اسکرپٹ لکھیں")
        script_text = st.text_area(
            "اردو میں کہانی یا اسکرپٹ لکھیں",
            placeholder="مثال: آج ہم آپ کو ایک خوبصورت کہانی سنائیں گے...",
            height=200,
            help="یہاں اپنی ویڈیو کا مکمل اسکرپٹ اردو میں لکھیں"
        )
        
        if script_text:
            word_count = len(script_text.split())
            st.info(f"📝 اسکرپٹ کے الفاظ: {word_count}")
            if word_count < 10:
                st.warning("⚠️ براہ کرم کم از کم 10 الفاظ کا اسکرپٹ لکھیں")
    
    # Process button
    process_button = st.button("🎬 ویڈیو بنانا شروع کریں", type="primary", use_container_width=True)
    
    if process_button:
        if not uploaded_videos or len(uploaded_videos) < 1:
            st.error("❌ براہ کرم کم از کم 1 ویڈیو کلپ اپ لوڈ کریں")
        elif not script_text or len(script_text.strip()) < 10:
            st.error("❌ براہ کرم کم از کم 10 الفاظ کا اسکرپٹ لکھیں")
        else:
            # Create progress tracking
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            try:
                # Step 1: Save uploaded videos
                status_placeholder.info("📁 ویڈیوز محفوظ کی جا رہی ہیں...")
                video_paths = []
                
                for uploaded_video in uploaded_videos:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                        tmp_file.write(uploaded_video.read())
                        video_paths.append(tmp_file.name)
                        st.session_state.temp_files.append(tmp_file.name)
                
                progress_placeholder.progress(0.2)
                status_placeholder.success(f"✅ {len(video_paths)} ویڈیوز محفوظ ہو گئیں")
                
                # Step 2: Generate voice
                status_placeholder.info("🎤 اردو آواز تیار کی جا رہی ہے...")
                voice_path = os.path.join(st.session_state.video_processor.temp_dir, "voice.mp3")
                
                if st.session_state.video_processor.generate_urdu_voice(script_text, voice_path):
                    progress_placeholder.progress(0.4)
                    status_placeholder.success("✅ اردو آواز تیار ہو گئی")
                else:
                    progress_placeholder.progress(0.4)
                    status_placeholder.warning("⚠️ آواز تیار کرنے میں مسئلہ، ویڈیو بغیر آواز کے بنے گی")
                    voice_path = None
                
                # Step 3: Combine videos
                status_placeholder.info("🎥 ویڈیوز کو ملایا جا رہا ہے (اس میں کچھ وقت لگ سکتا ہے)...")
                output_video_path = os.path.join(st.session_state.video_processor.temp_dir, "final_video.mp4")
                
                if st.session_state.video_processor.combine_videos(video_paths, output_video_path, voice_path):
                    progress_placeholder.progress(0.7)
                    status_placeholder.success("✅ ویڈیوز کامیابی سے مل گئیں")
                    
                    # Step 4: Generate thumbnail
                    status_placeholder.info("🖼️ تھمب نیل تیار کیا جا رہا ہے...")
                    thumbnail_path = os.path.join(st.session_state.video_processor.temp_dir, "thumbnail.jpg")
                    title = st.session_state.video_processor.generate_title(script_text)
                    
                    if st.session_state.video_processor.generate_thumbnail(output_video_path, thumbnail_path, title):
                        progress_placeholder.progress(0.9)
                        status_placeholder.success("✅ تھمب نیل تیار ہو گیا")
                    else:
                        progress_placeholder.progress(0.9)
                        status_placeholder.warning("⚠️ تھمب نیل تیار نہیں ہو سکا")
                        thumbnail_path = None
                    
                    # Get video duration
                    duration = st.session_state.video_processor.get_video_duration(output_video_path)
                    
                    # Generate metadata
                    description = st.session_state.video_processor.generate_description(script_text, duration, len(video_paths))
                    
                    progress_placeholder.progress(1.0)
                    status_placeholder.success("✅ ویڈیو کامیابی سے تیار ہو گئی!")
                    
                    # Display results
                    st.markdown('<div class="success-message">🎉 مبارک ہو! آپ کی ویڈیو تیار ہے۔</div>', unsafe_allow_html=True)
                    
                    # Create tabs for results
                    tab1, tab2, tab3 = st.tabs(["🎥 ویڈیو", "🖼️ تھمب نیل", "📝 معلومات"])
                    
                    with tab1:
                        st.subheader("تیار شدہ ویڈیو")
                        with open(output_video_path, 'rb') as video_file:
                            video_bytes = video_file.read()
                            st.video(video_bytes)
                        
                        # Download button
                        with open(output_video_path, 'rb') as f:
                            st.download_button(
                                label="📥 ویڈیو ڈاؤن لوڈ کریں",
                                data=f,
                                file_name=f"final_video_{int(time.time())}.mp4",
                                mime="video/mp4",
                                use_container_width=True
                            )
                    
                    with tab2:
                        if thumbnail_path and os.path.exists(thumbnail_path):
                            st.subheader("تھمب نیل")
                            with open(thumbnail_path, 'rb') as thumb_file:
                                thumb_bytes = thumb_file.read()
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
                        
                        # Download description
                        st.download_button(
                            label="📄 تفصیل ڈاؤن لوڈ کریں",
                            data=description,
                            file_name=f"description_{int(time.time())}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    st.balloons()
                    
                else:
                    status_placeholder.error("❌ ویڈیوز کو ملانے میں خرابی ہوئی")
                    
            except Exception as e:
                logger.error(f"Error in main process: {traceback.format_exc()}")
                st.error(f"❌ ایک خرابی پیش آ گئی: {str(e)}")
                st.info("براہ کرم دوبارہ کوشش کریں یا اپنے ویڈیوز کا سائز کم کریں")
            
            finally:
                # Clean up temporary files
                cleanup_temp_files()
    
    # Sidebar information
    with st.sidebar:
        st.markdown("## 📋 معلومات")
        st.markdown("""
        ### کیسے استعمال کریں:
        1. **ویڈیو کلپس اپ لوڈ کریں** - کم از کم 1 ویڈیو کلپ
        2. **اسکرپٹ لکھیں** - اردو میں کہانی یا اسکرپٹ
        3. **ویڈیو بنائیں** - بٹن دبائیں
        
        ### خصوصیات:
        - ✅ اردو آواز
        - ✅ ویڈیوز کو ملانا
        - ✅ آٹو تھمب نیل
        - ✅ آٹو ٹائٹل اور تفصیل
        - ✅ ڈاؤن لوڈ آپشن
        
        ### سپورٹڈ فارمیٹس:
        - MP4, AVI, MOV, MKV
        - زیادہ سے زیادہ 10 ویڈیوز
        - ہر ویڈیو کا زیادہ سے زیادہ سائز: 200MB
        
        ### نوٹ:
        - پہلی بار پروسیسنگ میں وقت لگ سکتا ہے
        - انٹرنیٹ کنیکشن ضروری ہے
        - اسکرپٹ صرف اردو میں لکھیں
        """)
        
        st.markdown("---")
        st.markdown("**🎬 ورژن:** 2.0")
        st.markdown("**👨‍💻 تیار کردہ:** AI Video Editor")
        
        # Add a clear cache button
        if st.button("🗑️ کیش صاف کریں"):
            cleanup_temp_files()
            st.success("کیش صاف ہو گیا")

if __name__ == "__main__":
    main()
