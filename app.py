import streamlit as st
import os
import tempfile
from pathlib import Path
import time
from video_processor import VideoProcessor
import json

# Page configuration
st.set_page_config(
    page_title="Video Editing System",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #ff4b4b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        color: #155724;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #e3f2fd;
        color: #0c5460;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<div class="main-header">🎬 Professional Video Editing System</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="info-box">📌 اس سسٹم میں آپ اپنی ویڈیوز اپ لوڈ کریں، اردو اسکرپٹ لکھیں، اور مکمل ویڈیو بنائیں۔</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'video_processor' not in st.session_state:
        st.session_state.video_processor = VideoProcessor()
    if 'videos_processed' not in st.session_state:
        st.session_state.videos_processed = False
    
    # Create columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 ویڈیو کلپس اپ لوڈ کریں")
        uploaded_videos = st.file_uploader(
            "5 یا اس سے زیادہ ویڈیو کلپس منتخب کریں",
            type=['mp4', 'avi', 'mov', 'mkv'],
            accept_multiple_files=True
        )
        
        if uploaded_videos:
            st.success(f"✅ {len(uploaded_videos)} ویڈیو کلپس اپ لوڈ ہو گئے")
            
            # Display video previews
            st.subheader("ویڈیوز کی تفصیلات:")
            for i, video in enumerate(uploaded_videos[:3], 1):  # Show first 3 only
                st.write(f"{i}. {video.name} - {video.size / 1024 / 1024:.2f} MB")
            if len(uploaded_videos) > 3:
                st.write(f"... اور {len(uploaded_videos) - 3} مزید")
    
    with col2:
        st.subheader("📝 ویڈیو اسکرپٹ لکھیں")
        script_text = st.text_area(
            "اردو میں کہانی یا اسکرپٹ لکھیں",
            placeholder="یہاں اپنی ویڈیو کا اسکرپٹ اردو میں لکھیں...",
            height=200
        )
        
        if script_text:
            st.info(f"📝 اسکرپٹ کے الفاظ: {len(script_text.split())}")
    
    # Process button
    if st.button("🎬 ویڈیو بنائیں", type="primary", use_container_width=True):
        if not uploaded_videos or len(uploaded_videos) < 1:
            st.error("❌ براہ کرم کم از کم 1 ویڈیو کلپ اپ لوڈ کریں")
        elif not script_text:
            st.error("❌ براہ کرم اسکرپٹ لکھیں")
        else:
            with st.spinner("🔄 ویڈیو پروسیسنگ جاری ہے... براہ کرم انتظار کریں"):
                try:
                    # Save uploaded videos temporarily
                    video_paths = []
                    for uploaded_video in uploaded_videos:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                            tmp_file.write(uploaded_video.read())
                            video_paths.append(tmp_file.name)
                    
                    # Generate voice
                    voice_path = os.path.join(st.session_state.video_processor.temp_dir, "voice.mp3")
                    if st.session_state.video_processor.generate_urdu_voice(script_text, voice_path):
                        st.success("✅ آواز تیار ہو گئی")
                    else:
                        st.warning("⚠️ آواز تیار کرنے میں مسئلہ، ویڈیو بغیر آواز کے بنے گی")
                        voice_path = None
                    
                    # Combine videos
                    output_video_path = os.path.join(st.session_state.video_processor.temp_dir, "final_video.mp4")
                    
                    progress_bar = st.progress(0)
                    st.write("🎥 ویڈیوز کو ملایا جا رہا ہے...")
                    
                    if st.session_state.video_processor.combine_videos(video_paths, output_video_path, voice_path):
                        progress_bar.progress(50)
                        st.success("✅ ویڈیوز کامیابی سے مل گئیں")
                        
                        # Generate thumbnail
                        thumbnail_path = os.path.join(st.session_state.video_processor.temp_dir, "thumbnail.jpg")
                        title = st.session_state.video_processor.generate_title(script_text)
                        
                        progress_bar.progress(75)
                        st.write("🖼️ تھمب نیل تیار کیا جا رہا ہے...")
                        
                        if st.session_state.video_processor.generate_thumbnail(output_video_path, thumbnail_path, title):
                            st.success("✅ تھمب نیل تیار ہو گیا")
                        
                        # Get video duration
                        from moviepy.editor import VideoFileClip
                        video_clip = VideoFileClip(output_video_path)
                        duration = video_clip.duration
                        video_clip.close()
                        
                        # Generate description and title
                        description = st.session_state.video_processor.generate_description(script_text, duration, len(video_paths))
                        title = st.session_state.video_processor.generate_title(script_text)
                        
                        progress_bar.progress(100)
                        
                        # Display results
                        st.markdown('<div class="success-message">✅ ویڈیو کامیابی سے تیار ہو گئی!</div>', unsafe_allow_html=True)
                        
                        # Display video
                        st.subheader("🎥 تیار شدہ ویڈیو")
                        with open(output_video_path, 'rb') as video_file:
                            video_bytes = video_file.read()
                            st.video(video_bytes)
                        
                        # Display thumbnail
                        st.subheader("🖼️ تھمب نیل")
                        with open(thumbnail_path, 'rb') as thumb_file:
                            thumb_bytes = thumb_file.read()
                            st.image(thumb_bytes, use_column_width=True)
                        
                        # Display title
                        st.subheader("📌 ویڈیو ٹائٹل")
                        st.markdown(f"**{title}**")
                        
                        # Display description
                        st.subheader("📝 ویڈیو تفصیل")
                        st.markdown(description)
                        
                        # Download buttons
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            with open(output_video_path, 'rb') as f:
                                st.download_button(
                                    label="📥 ویڈیو ڈاؤن لوڈ کریں",
                                    data=f,
                                    file_name=f"final_video_{int(time.time())}.mp4",
                                    mime="video/mp4"
                                )
                        
                        with col2:
                            with open(thumbnail_path, 'rb') as f:
                                st.download_button(
                                    label="🖼️ تھمب نیل ڈاؤن لوڈ کریں",
                                    data=f,
                                    file_name=f"thumbnail_{int(time.time())}.jpg",
                                    mime="image/jpeg"
                                )
                        
                        with col3:
                            description_file = f"description_{int(time.time())}.txt"
                            st.download_button(
                                label="📄 تفصیل ڈاؤن لوڈ کریں",
                                data=description,
                                file_name=description_file,
                                mime="text/plain"
                            )
                        
                        # Clean up temporary files
                        for video_path in video_paths:
                            try:
                                os.unlink(video_path)
                            except:
                                pass
                        
                        st.balloons()
                        
                    else:
                        st.error("❌ ویڈیوز کو ملانے میں خرابی ہوئی")
                        
                except Exception as e:
                    st.error(f"❌ ایک خرابی پیش آ گئی: {str(e)}")
                    st.write("براہ کرم دوبارہ کوشش کریں")
    
    # Sidebar information
    with st.sidebar:
        st.markdown("## 📋 معلومات")
        st.markdown("""
        ### کیسے استعمال کریں:
        1. **ویڈیو کلپس اپ لوڈ کریں** - کم از کم 1 ویڈیو کلپ
        2. **اسکرپٹ لکھیں** - اردو میں کہانی یا اسکرپٹ
        3. **ویڈیو بنائیں** - بٹن دبائیں
        
        ### خصوصیات:
        - ✅ اردو آواز (مردانہ آواز)
        - ✅ ویڈیوز کو ملانا
        - ✅ آٹو تھمب نیل جنریشن
        - ✅ ویڈیو ٹائٹل اور تفصیل
        - ✅ ڈاؤن لوڈ آپشن
        
        ### نوٹ:
        - سپورٹڈ فارمیٹس: MP4, AVI, MOV, MKV
        - زیادہ سے زیادہ 10 ویڈیوز
        - اسکرپٹ صرف اردو میں
        """)
        
        st.markdown("---")
        st.markdown("**🎬 ورژن:** 1.0")
        st.markdown("**👨‍💻 ڈویلپر:** AI Video Editor")

if __name__ == "__main__":
    main()
