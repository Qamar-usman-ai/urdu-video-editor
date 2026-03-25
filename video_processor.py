from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import os
import random


def merge_clips(video_paths, output_path="merged.mp4"):
    clips = [VideoFileClip(v) for v in video_paths]
    final = concatenate_videoclips(clips)
    final.write_videofile(output_path, codec="libx264")
    return output_path


def generate_voice(script_text, output_audio="voice.mp3"):
    tts = gTTS(text=script_text, lang='ur')
    tts.save(output_audio)
    return output_audio


def add_voice_to_video(video_path, audio_path, output_path="final_video.mp4"):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    video = video.set_audio(audio)
    video.write_videofile(output_path, codec="libx264")
    return output_path


def generate_thumbnail(text, output_path="thumbnail.png"):
    img = Image.new('RGB', (1280, 720), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()

    draw.text((50, 300), text[:40], fill=(255, 255, 255), font=font)
    img.save(output_path)
    return output_path


def generate_title(script):
    return "Amazing Story: " + script[:30]


def generate_description(script):
    return "This video is about: " + script
