from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Form, UploadFile, File

from typing import Optional
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/calculate")
async def calculate_client_input(
        data: str = Form(...),
        file: Optional[UploadFile] = File(None)
    ):
    request_data = json.loads(data)
    
    regions = request_data.get('regions', [])
    metrics = request_data.get('metrics', [])
    settings = request_data.get('settings', [])
    timestamp1 = request_data.get('timestamp1', {})
    timestamp2 = request_data.get('timestamp2', {})

    print("Пришли данные:", regions, metrics, settings, timestamp1, timestamp2)

    if file:
        print("Даже есть какой-то файл")

    return {
        "status": "success",
        "data": {"numbers": [1, 2, 3, 4, 5]},
        "message": "Данные успешно обработаны"
    }

