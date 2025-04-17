import os
import tempfile
import whisper
import requests
from flask import Flask, request, jsonify, send_file
from elevenlabs import generate, set_api_key
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip

app = Flask(__name__)

# Carregamento do modelo Whisper
model = whisper.load_model("base")

# ElevenLabs API
set_api_key("sk-8f4822d2b6d38192cdf02ee1987d7aeb2912ac550c63b63f")

def transcribe_audio(audio_path):
    result = model.transcribe(audio_path)
    return result["text"]

def generate_voice(text, voice="Rachel"):
    audio = generate(text=text, voice=voice, model="eleven_multilingual_v2")
    temp_audio_path = tempfile.mktemp(suffix=".mp3")
    with open(temp_audio_path, "wb") as f:
        f.write(audio)
    return temp_audio_path

def extract_audio(video_path):
    video = VideoFileClip(video_path)
    audio_path = tempfile.mktemp(suffix=".mp3")
    video.audio.write_audiofile(audio_path)
    return audio_path

def replace_audio(video_path, new_audio_path):
    video = VideoFileClip(video_path)
    new_audio = AudioFileClip(new_audio_path).set_duration(video.duration)
    video = video.set_audio(new_audio)
    output_path = tempfile.mktemp(suffix=".mp4")
    video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path

@app.route("/dub", methods=["POST"])
def dub_video():
    if "video" not in request.files:
        return jsonify({"error": "No video uploaded"}), 400

    file = request.files["video"]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        file.save(temp_video.name)

    original_audio_path = extract_audio(temp_video.name)
    transcription = transcribe_audio(original_audio_path)
    new_audio_path = generate_voice(transcription)
    output_video_path = replace_audio(temp_video.name, new_audio_path)

    return send_file(output_video_path, mimetype="video/mp4")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")