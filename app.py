import streamlit as st
import os
from video_utils import *

st.title("🎬 AI Video Generator")

uploaded_videos = st.file_uploader("Upload Video Clips", type=["mp4"], accept_multiple_files=True)
script_file = st.file_uploader("Upload Script (.txt)", type=["txt"])

if st.button("Generate Video"):
    if uploaded_videos and script_file:
        os.makedirs("temp", exist_ok=True)

        video_paths = []
        for i, vid in enumerate(uploaded_videos):
            path = f"temp/video_{i}.mp4"
            with open(path, "wb") as f:
                f.write(vid.read())
            video_paths.append(path)

        script_text = script_file.read().decode("utf-8")

        st.info("Merging videos...")
        merged_video = merge_clips(video_paths)

        st.info("Generating Urdu voice...")
        audio = generate_voice(script_text)

        st.info("Adding voice to video...")
        final_video = add_voice_to_video(merged_video, audio)

        st.info("Generating thumbnail...")
        thumbnail = generate_thumbnail(script_text)

        title = generate_title(script_text)
        description = generate_description(script_text)

        st.success("Done!")

        st.video(final_video)
        st.image(thumbnail)

        st.write("### Title")
        st.write(title)

        st.write("### Description")
        st.write(description)

    else:
        st.error("Please upload videos and script")
