from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.crud import create_custom_game

app = FastAPI(title="UzChess Web App API")

# HTML andozalar (templates) turgan papkani tanitamiz
templates = Jinja2Templates(directory="webapp/templates")

# Brauzer xavfsizlik cheklovlarini (CORS) ochamiz
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ma'lumotlar bazasiga ulanish uchun yordamchi
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Foydalanuvchi Web App'ni ochganda index.html sahifasini ko'rsatish (Frontend eshigi)
@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    # TypeError xatoligini oldini olish uchun argumentlar nomi bilan uzatiladi
    return templates.TemplateResponse(request=request, name="index.html")

# 2. O'yinchi Web App'da o'yin yaratganda chaqiriladigan API yo'li (Backend endpointi)
@app.post("/api/game/create")
def api_create_game(creator_id: int, time_limit: int, chosen_color: str, db: Session = Depends(get_db)):
    try:
        game = create_custom_game(db, creator_id=creator_id, time_limit=time_limit, chosen_color=chosen_color)
        return {
            "status": "success",
            "game_id": game.id,
            "message": "O'yin muvaffaqiyatli yaratildi. Endi do'stingizga havola yuborishingiz mumkin!"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))