import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database.database import SessionLocal
from database.crud import get_or_create_user

TOKEN = "8831656585:AAGoaoYsV-k5DSSexiXkNZFTPFqNgbdgH8I"

# MAJBURIY OBUNA KANALI (Buni o'zingizning kanalingizga almashtiring)
REQUIRED_CHANNEL = "-1003900981353"  # yoki kanal ID si: -100xxxxxxxxx

# Kanalga a'zolikni tekshiruvchi funksiya
async def check_subscription(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception:
        # Agar kanal topilmasa yoki bot administrator bo'lmasa, o'yin to'xtab qolmasligi uchun True beramiz
        return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_user = update.effective_user
    user_id = tg_user.id
    
    # 1. Havola bilan kelgan (Taklif qilingan) o'yinchini aniqlash
    args = context.args
    game_id = None
    if args and args[0].startswith("game_"):
        game_id = args[0].split("_")[1]

    # Ma'lumotlar bazasida ro'yxatdan o'tkazish
    db = SessionLocal()
    user = get_or_create_user(db, telegram_id=user_id, username=tg_user.username)
    db.close()

    # 2. Kanalga obunani tekshirish
    is_subscribed = await check_subscription(context.bot, user_id)
    if not is_subscribed:
        # Agar obuna bo'lmagan bo'lsa, majburiy havola beramiz
        await update.message.reply_text(
            f"Diqqat! 🛑 O'yinga kirish uchun birinchi navbatda rasmiy kanalimizga a'zo bo'ling:\n\n"
            f"👉 {REQUIRED_CHANNEL}\n\n"
            f"A'zo bo'lgach, qaytadan /start buyrug'ini bosing!"
        )
        return

    # Agar taklif havolasi orqali kelgan bo'lsa va obunadan o'tgan bo'lsa:
    if game_id:
        await update.message.reply_text(
            f"Ajoyib! 🎉 Siz {game_id}-raqamli o'yin taklifini qabul qildingiz.\n"
            f"Raqibingiz sizni kutmoqda! O'yin sahifasi yuklanmoqda... ⚔️"
        )
        # Bu yerda keyinchalik o'yin o'ynaladigan Mini App manzilini ham ochish mumkin
        return

    # Standart menyu
    if os.environ.get("PORT"):
        web_app_url = "https://uzchessbot.onrender.com/"
    else:
        web_app_url = "http://127.0.0.1:8000/"

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

# "Kompyuterga qarshi" yoki "Reyting" tugmalari bosilganda ishlaydigan mantiq
async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Kompyuterga qarshi 🤖":
        # Kompyuter bilan o'ynash uchun maxsus WebApp sahifasi (kelajakda ochiladigan qism)
        await update.message.reply_text(
            "🤖 Kompyuterga qarshi o'yin tizimi yuklanmoqda...\n"
            "Tez orada Stockfish botiga qarshi daxshatli o'yinlarni boshlaysiz!"
        )
    elif text == "Reyting 🏆":
        await update.message.reply_text("🏆 Global reyting peshqadamlari ro'yxati tez orada shu yerda ko'rinadi.")

def run_bot():
    print("Bot ishga tushmoqda...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    # Matnli tugmalarni ushlab qolish uchun handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_buttons))
    
    app.run_polling()

if __name__ == "__main__":
    run_bot()