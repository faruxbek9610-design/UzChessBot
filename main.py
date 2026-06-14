import os
import uvicorn
from database.database import init_db
from webapp.app import app
from bot.bot import init_telegram_webhook

if __name__ == "__main__":
    print("1. Ma'lumotlar bazasi tekshirilmoqda...")
    init_db()
    
    # Render muhitini tekshiramiz
    PORT = int(os.environ.get("PORT", 8000))
    
    if os.environ.get("PORT"):
        print("2. Render muhitida Telegram Webhook sozlanmoqda...")
        # Bot Webhook rejimida daxshatli tez ishlashi uchun FastAPI ishga tushishidan oldin ishlaydi
        init_telegram_webhook(app)
    else:
        print("2. Lokal muhit (Polling rejimida sinov uchun)...")
        # Lokal kompyuterda sinash uchun alohida tarmoqda polling ishga tushadi
        import threading
        from bot.bot import run_bot_polling
        polling_thread = threading.Thread(target=run_bot_polling, daemon=True)
        polling_thread.start()

    print("3. Uvicorn veb-serveri ishga tushirilmoqda...")
    # Render uchun host "0.0.0.0" bo'lishi shart!
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, log_level="info")