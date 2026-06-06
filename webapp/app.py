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

# 1. Foydalanuvchi Web App'ni ochganda index.html sahifasini ko'rsatish
@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# 2. O'yinchi Web App'da o'yin yaratganda chaqiriladigan API yo'li
@app.post("/api/game/create")
def api_create_game(creator_id: int, time_limit: int, chosen_color: str, db: Session = Depends(get_db)):
    try:
        # Ma'lumotlar bazasida o'yin yaratamiz
        game = create_custom_game(db, creator_id=creator_id, time_limit=time_limit, chosen_color=chosen_color)
        
        # 🔥 DIQQAT: Bot yuzerneymi sizniki bilan almashtirildi!
        game_url = f"https://t.me/UzCheess_bot/app?startapp=game_{game.id}"
        
        return {
            "status": "success",
            "game_id": game.id,
            "game_url": game_url,
            "message": "O'yin muvaffaqiyatli yaratildi! Havolani nusxalab do'stingizga yuboring."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))