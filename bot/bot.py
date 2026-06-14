import os
import json
from contextlib import asynccontextmanager
from fastapi import Request, Response, FastAPI
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from database.database import SessionLocal
from database.crud import get_or_create_user

TOKEN = "8831656585:AAE8yeqGju6sZJopRcNWVJJqoTdLDf4Jl6U"

# 🔥 KANAL SOZLAMALARI
CHANNEL_ID = -1003900981353      
CHANNEL_USERNAME = "@UzCheess"

# Global application obyekti
telegram_app = Application.builder().token(TOKEN).build()

# Webhook path (Xavfsizlik uchun token bilan)
WEBHOOK_PATH = f"/webhook/{TOKEN}"

# Kanalga a'zolikni tekshirish
async def check_subscription(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        print(f"Obunani tekshirishda xatolik: {e}")
        return False

# Asosiy menyu
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user, tg_user):
    # Render loyiha havolasi yoki lokal xost
    web_app_url = "https://uzchessbot.onrender.com/" if os.environ.get("PORT") else "http://127.0.0.1:8000/"

    keyboard = [
        [
            KeyboardButton("Do'st bilan o'yin ⚔️", web_app=WebAppInfo(url=web_app_url)),
            KeyboardButton("Tasodifiy o'yin 🎮", web_app=WebAppInfo(url=web_app_url))
        ],
        [
            KeyboardButton("Kompyuterga qarshi 🤖"),
            KeyboardButton("Reyting 🏆")
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    text = (
        f"Salom, {tg_user.first_name}! 👋\n"
        f"Uz Chess Match platformasiga xush kelibsiz!\n\n"
        f"🏅 Sizning reytingingiz: {user.elo_rating}\n"
        f"💰 Tangalaringiz: {user.coins}\n\n"
        f"O'yin turini tanlang va shaxmat olamiga sho'ng'ing!"
    )
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup)

# /start buyrug'i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_user = update.effective_user
    user_id = tg_user.id
    
    # Mini App'dan startapp orqali kelgan game_id ni aniqlash
    args = context.args
    game_id = None
    if args and args[0]:
        game_id = args[0]

    db = SessionLocal()
    user = get_or_create_user(db, telegram_id=user_id, username=tg_user.username)
    db.close()

    is_subscribed = await check_subscription(context.bot, user_id)
    if not is_subscribed:
        callback_data = f"check_sub_game_{game_id}" if game_id else "check_sub_none"
        
        keyboard = [
            [InlineKeyboardButton("Kanalga a'zo bo'lish 🚀", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton("A'zo bo'ldim ✅", callback_data=callback_data)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Diqqat! 🛑 O'yinga kirish uchun birinchi navbatda rasmiy kanalimizga a'zo bo'ling:\n\n"
            f"👉 {CHANNEL_USERNAME}\n\n"
            f"A'zo bo'lib, pastdagi yashil tugmani bosing 👇",
            reply_markup=reply_markup
        )
        return

    if game_id:
        web_app_url = f"https://uzchessbot.onrender.com/?g={game_id}" if os.environ.get("PORT") else f"http://127.0.0.1:8000/?g={game_id}"
        keyboard = [[InlineKeyboardButton("🎮 Jangga qo'shilish", web_app=WebAppInfo(url=web_app_url))]]
        
        await update.message.reply_text(
            f"Ajoyib! 🎉 Siz shaxmat jangi taklifini qabul qildingiz.\n"
            f"Raqibingiz sizni kutmoqda! Quyidagi tugmani bosib daxshatli jangga kiring 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await show_main_menu(update, context, user, tg_user)

# Obunani tekshirish Callback
async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    tg_user = query.from_user
    
    is_subscribed = await check_subscription(context.bot, user_id)
    
    if is_subscribed:
        try: await query.message.delete()
        except Exception: pass
        
        db = SessionLocal()
        user = get_or_create_user(db, telegram_id=user_id, username=tg_user.username)
        db.close()
        
        data = query.data
        if data.startswith("check_sub_game_") and not data.endswith("none"):
            game_id = data.split("_")[3]
            web_app_url = f"https://uzchessbot.onrender.com/?g={game_id}" if os.environ.get("PORT") else f"http://127.0.0.1:8000/?g={game_id}"
            keyboard = [[InlineKeyboardButton(" O'yinga kirish", web_app=WebAppInfo(url=web_app_url))]]
            await query.message.reply_text(
                f"Tabriklaymiz! 🎉 Obuna muvaffaqiyatli tekshirildi.\n"
                f"O'yin xonangiz tayyor! Quyidagi tugma orqali jangga qo'shiling 👇",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.message.reply_text("Rahmat! Botdan to'liq foydalanishingiz mumkin. 🎉")
            await show_main_menu(update, context, user, tg_user)
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"Siz hali ham {CHANNEL_USERNAME} kanaliga a'zo bo'lmadingiz. ❌\nIltimos, oldin a'zo bo'ling."
        )

# Menyu tugmalari mantig'i
async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Kompyuterga qarshi 🤖":
        await update.message.reply_text(
            "🤖 Kompyuterga (Botga) qarshi o'yin tizimi daxshatli yangilandi!\n"
            "Asosiy menyudagi 'Do'st bilan o'yin' yoki 'Tasodifiy o'yin' tugmalarini bosing va ochilgan oyna ichidan 'Kompyuter (Bot) bilan' degan ko'k tugmani tanlang! Oflayn tizim ishga tushadi! 🔥"
        )
    elif text == "Reyting 🏆":
        await update.message.reply_text("🏆 Global reyting peshqadamlari ro'yxati tez orada shu yerda mukammal ko'rinadi.")

# --- HANDLERLARNI RO'YXATDAN O'TKAZISH ---
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(check_sub_callback, pattern="^check_sub_"))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_buttons))


# 🔥 MODERNIY LIFESPAN DIZAYNI (Eski add_event_handler o'rniga)
@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    # ---- STARTUP: Server yoqqanda faqat 1 marta ishlaydi ----
    PORT_ENV = os.environ.get("PORT")
    
    # Bot tizimini 1 marta to'liq initsializatsiya qilamiz
    await telegram_app.initialize()
    
    if PORT_ENV:
        print("-> [Lifespan] Render muhiti. Telegram Webhook sozlanmoqda...")
        RENDER_URL = "https://uzchessbot.onrender.com"
        full_webhook_url = f"{RENDER_URL}{WEBHOOK_PATH}"
        
        await telegram_app.bot.set_webhook(url=full_webhook_url)
        print(f"✅ Webhook o'rnatildi: {full_webhook_url}")
    else:
        print("-> [Lifespan] Lokal muhit. Polling ishga tushmoqda...")
        await telegram_app.start()
        import asyncio
        asyncio.create_task(telegram_app.updater.start_polling())
        print("✅ Polling fonda muvaffaqiyatli boshlandi!")

    yield  # <-- Shu joyda FastAPI kelayotgan so'rovlarni (HTTP va Webhook) qabul qilishni boshlaydi

    # ---- SHUTDOWN: Server o'chirilganda xavfsiz yopiladi ----
    print("-> [Lifespan] Server o'chmoqda. Bot jarayonlari to'xtatilmoqda...")
    if not PORT_ENV:
        await telegram_app.updater.stop()
        await telegram_app.stop()
    await telegram_app.shutdown()
    print("✅ Bot xavfsiz yopildi.")


# FastAPI uchun Webhook routerini sozlash funkiyasi
def init_telegram_webhook(fastapi_app: FastAPI):
    @fastapi_app.post(WEBHOOK_PATH)
    async def telegram_webhook_endpoint(request: Request):
        try:
            req_body = await request.json()
            update = Update.de_json(req_body, telegram_app.bot)
            # Lifespan ichida initialize qilingani sababli faqat update'ni yuboramiz
            await telegram_app.process_update(update)
        except Exception as e:
            print(f"❌ Webhook ichida xatolik: {e}")
        return Response(status_code=200)