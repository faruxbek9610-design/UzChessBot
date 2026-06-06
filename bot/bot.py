import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
from database.database import SessionLocal
from database.crud import get_or_create_user

# @BotFather'dan olgan tokeningiz:
TOKEN = "8831656585:AAGoaoYsV-k5DSSexiXkNZFTPFqNgbdgH8I"

# Botga /start buyrug'i berilganda ishlaydigan funksiya
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_user = update.effective_user
    telegram_id = tg_user.id
    username = tg_user.username

    # Ma'lumotlar bazasiga ulanamiz va foydalanuvchini ro'yxatdan o'tkazamiz
    db = SessionLocal()
    user = get_or_create_user(db, telegram_id=telegram_id, username=username)
    db.close()

    # DIQQAT: Render'da https ishlasa onlayn url, lokal kompyuterda http ishlaydi
    # Bu usul loyihangizni ham uydagi kompyuterda, ham serverda xatosiz yurgizadi!
    if os.environ.get("PORT"):
        web_app_url = "https://uzchessbot.onrender.com/"
    else:
        web_app_url = "http://127.0.0.1:8000/"

    # Telegram bot ichida oynani ochadigan maxsus WebApp tugmalari
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
    
    await update.message.reply_text(text, reply_markup=reply_markup)

# Botni ishga tushirish funksiyasi
def run_bot():
    print("Bot ishga tushmoqda...")
    app = Application.builder().token(TOKEN).build()
    
    # /start komandasini botga ulaymiz
    app.add_handler(CommandHandler("start", start))
    
    # Botni tinimsiz xabar kutish rejimiga o'tkazamiz
    app.run_polling()

if __name__ == "__main__":
    run_bot()