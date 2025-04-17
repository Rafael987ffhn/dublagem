
from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
import uuid
import whisper
import requests
from pydub import AudioSegment

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

model = whisper.load_model("base")

ELEVENLABS_API_KEY = "sk-8f4822d2b6d38192cdf02ee1987d7aeb2912ac550c63b63f"
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Você pode mudar depois

@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process")
async def process(request: Request, file: UploadFile, language: str = Form(...)):
    temp_video = f"temp_{uuid.uuid4()}.mp4"
    temp_audio = temp_video.replace(".mp4", ".mp3")
    temp_dubbed_audio = temp_video.replace(".mp4", "_dubbed.mp3")
    final_video = temp_video.replace(".mp4", "_dubbed.mp4")

    with open(temp_video, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extrai o áudio
    audio = AudioSegment.from_file(temp_video)
    audio.export(temp_audio, format="mp3")

    # Transcrição com Whisper
    result = model.transcribe(temp_audio, language=language)
    transcription = result["text"]

    # Geração de áudio com ElevenLabs
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": transcription,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        json=payload,
        headers=headers
    )

    with open(temp_dubbed_audio, "wb") as f:
        f.write(response.content)

    # Substituir o áudio original pelo dublado
    from moviepy.editor import VideoFileClip, AudioFileClip
    video = VideoFileClip(temp_video)
    audio = AudioFileClip(temp_dubbed_audio)
    final = video.set_audio(audio)
    final.write_videofile(final_video)

    return FileResponse(final_video, media_type="video/mp4", filename="dubbed_video.mp4")
