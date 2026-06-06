import threading
import uvicorn
from database.database import init_db
from bot.bot import run_bot

# FastAPI veb-serverini ishga tushiradigan funksiya
def start_fastapi():
    print("-> FastAPI veb-serveri ishga tushmoqda...")
    # webapp papkasidagi app faylidan app obyektini ishga tushiramiz
    uvicorn.run("webapp.app:app", host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    print("1. Ma'lumotlar bazasi tekshirilmoqda...")
    init_db()
    
    # FastAPI'ni alohida tarmoqda (thread) ishga tushiramiz
    # Bu bot ishlashiga xalaqit bermasligi uchun kerak
    api_thread = threading.Thread(target=start_fastapi, daemon=True)
    api_thread.start()
    
    print("2. Telegram bot ishga tushirilmoqda...")
    # Botni asosiy tarmoqda ishga tushiramiz
    run_bot()