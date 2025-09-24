from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Привет от FastAPI!"}

# Эндпоинт для кнопки, который возвращает значение
@app.get("/api/button-click")
def handle_button_click():
    # Здесь может быть сложная логика
    return {"response": "Кнопка была нажата! Сервер отвечает."}

