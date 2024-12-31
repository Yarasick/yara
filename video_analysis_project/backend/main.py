from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import ffmpeg
import whisper
from ultralytics import YOLO
import cv2

app = FastAPI()

# Дозвіл CORS (якщо потрібно для доступу з браузера)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статичні файли (для HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Ініціалізація моделей
whisper_model = whisper.load_model("large-v2")
yolo_model = YOLO("yolov8n.pt")

# Створення директорії для завантаження файлів
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/analyze/")
async def analyze_video(file: UploadFile = File(...)):
    # Збереження відео
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())

    # Витягнення аудіо з відео
    audio_path = filepath.replace(".mp4", ".mp3")
    ffmpeg.input(filepath).output(audio_path).run()

    # Транскрипція
    transcription_result = whisper_model.transcribe(audio_path)
    transcription = transcription_result["text"]

    # Аналіз кадрів відео
    cap = cv2.VideoCapture(filepath)
    detections = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        yolo_results = yolo_model(frame)
        detections.append(yolo_results[0].pandas().xyxy.to_dict(orient="records"))
    cap.release()

    # Видалення тимчасових файлів
    os.remove(filepath)
    os.remove(audio_path)

    return {"transcription": transcription, "detections": detections}
