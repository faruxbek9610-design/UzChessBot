import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from telegram.ext import Application

# Bot obyektingiz (Mavjud kodlar asosida)
# TOKEN = "..."
# application = Application.builder().token(TOKEN).build()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP: Server ishga tushganda bajariladigan qism ---
    PORT_ENV = os.environ.get("PORT")
    
    if PORT_ENV:
        print("-> [Lifespan] Render muhiti aniqlandi. Webhook sozlanmoqda...")
        RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "")
        
        if RENDER_EXTERNAL_URL:
            webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
            await application.initialize()
            await application.bot.set_webhook(url=webhook_url)
            print(f"✅ [Webhook] Muvaffaqiyatli o'rnatildi: {webhook_url}")
        else:
            print("⚠️ [Webhook] RENDER_EXTERNAL_URL topilmadi! Webhook o'rnatilmadi.")
    else:
        print("-> [Lifespan] Lokal muhit aniqlandi. Polling rejimida bot ishga tushmoqda...")
        await application.initialize()
        await application.start()
        # Polling'ni asynchronous tarzda fonda boshlaymiz
        import asyncio
        asyncio.create_task(application.updater.start_polling())
        print("✅ [Polling] Bot lokal rejimda xabarlarni tinglamoqda...")

    yield  # <-- Shu yerda FastAPI ilovasi so'rovlarni qabul qilishni boshlaydi

    # --- SHUTDOWN: Server o'chganda bajariladigan qism ---
    print("-> [Lifespan] Server to'xtatilmoqda. Bot tozalanyapti...")
    if not PORT_ENV:
        await application.updater.stop()
        await application.stop()
    await application.shutdown()
    print("✅ [Lifespan] Bot xavfsiz to'xtatildi.")