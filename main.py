import os
import threading
import uvicorn
from database.database import init_db
from bot.bot import run_bot

# FastAPI veb-serverini ishga tushiradigan funksiya
def start_fastapi():
    print("-> FastAPI veb-serveri ishga tushmoqda...")
    
    # Render serveri taqdim etadigan portni o'qiymiz, agar topilmasa (lokalda) 8000 ni oladi
    port = int(os.environ.get("PORT", 8000))
    
    # Render uchun host "0.0.0.0" bo'lishi shart!
    uvicorn.run("webapp.app:app", host="0.0.0.0", port=port, log_level="info")

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