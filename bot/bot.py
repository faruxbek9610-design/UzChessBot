import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from database.database import SessionLocal
from database.crud import get_or_create_user

TOKEN = "8831656585:AAGoaoYsV-k5DSSexiXkNZFTPFqNgbdgH8I"

# 🌟 BU YERGA O'ZINGIZNING KANAL USERNAME'INGIZNI YOZING (Masalan: @uzchess_news)
REQUIRED_CHANNEL = "@https://t.me/UzCheess" 

# Kanalga a'zolikni tekshiruvchi funksiya
async def check_subscription(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        print(f"Obunani tekshirishda xatolik: {e}")
        # Agar bot kanalga admin bo'lmasa yoki kanal topilmasa, xatolik bermay o'tkazib yuboradi
        return True

# Standart asosiy menyuni chiqaruvchi yordamchi funksiya
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user, tg_user):
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
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup)

# /start buyrug'i kelganda
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_user = update.effective_user
    user_id = tg_user.id
    
    # Havola orqali kelgan o'yin ID sini aniqlash
    args = context.args
    game_id = None
    if args and args[0].startswith("game_"):
        game_id = args[0].split("_")[1]

    # Ma'lumotlar bazasida foydalanuvchini tekshirish/yaratish
    db = SessionLocal()
    user = get_or_create_user(db, telegram_id=user_id, username=tg_user.username)
    db.close()

    # Kanalga obunani tekshirish
    is_subscribed = await check_subscription(context.bot, user_id)
    if not is_subscribed:
        # Kanal havolasi bilan chiroyli Inline tugma va ostida "A'zo bo'ldim" tasdiqlash tugmasi
        # Agar do'stlik linki bo'lsa, uni callback ichiga yashirib ketamiz, a'zo bo'lgach adashmaslik uchun
        callback_data = f"check_sub_game_{game_id}" if game_id else "check_sub_none"
        
        keyboard = [
            [InlineKeyboardButton("Kanalga a'zo bo'lish 🚀", url=f"https://t.me/{REQUIRED_CHANNEL.replace('@', '')}")],
            [InlineKeyboardButton("A'zo bo'ldim ✅", callback_data=callback_data)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Diqqat! 🛑 O'yinga kirish uchun birinchi navbatda rasmiy kanalimizga a'zo bo'ling:\n\n"
            f"👉 {REQUIRED_CHANNEL}\n\n"
            f"A'zo bo'lib, pastdagi yashil tugmani bosing 👇",
            reply_markup=reply_markup
        )
        return

    # Agar allaqachon a'zo bo'lsa va o'yin linkidan kelgan bo'lsa
    if game_id:
        await update.message.reply_text(
            f"Ajoyib! 🎉 Siz {game_id}-raqamli o'yin taklifini qabul qildingiz.\n"
            f"Raqibingiz sizni kutmoqda! O'yin sahifasi yuklanmoqda... ⚔️"
        )
        return

    # Standart kirish
    await show_main_menu(update, context, user, tg_user)

# "A'zo bo'ldim ✅" tugmasi bosilganda ishlaydigan mantiq
async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Tugma yuklanishini to'xtatish
    
    user_id = query.from_user.id
    tg_user = query.from_user
    
    # Kanalga a'zolikni qayta tekshiramiz
    is_subscribed = await check_subscription(context.bot, user_id)
    
    if is_subscribed:
        # Eski ogohlantirish xabarini o'chirib tashlaymiz
        await query.message.delete()
        
        db = SessionLocal()
        user = get_or_create_user(db, telegram_id=user_id, username=tg_user.username)
        db.close()
        
        # Callback ma'lumotidan o'yin ID sini qidiramiz
        data = query.data
        if data.startswith("check_sub_game_") and not data.endswith("None"):
            game_id = data.split("_")[3]
            await query.message.reply_text(
                f"Tabriklaymiz! 🎉 Obuna muvaffaqiyatli tekshirildi.\n"
                f"Siz {game_id}-raqamli o'yin taklifini qabul qildingiz. O'yin boshlanmoqda... ⚔️"
            )
        else:
            # Oddiy kirgan bo'lsa, asosiy menyuni ochamiz
            await query.message.reply_text("Rahmat! Botdan to'liq foydalanishingiz mumkin. 🎉")
            await show_main_menu(update, context, user, tg_user)
    else:
        # Agar hali ham a'zo bo'lmagan bo'lsa, ogohlantirish chiqaramiz
        await context.bot.send_message(
            chat_id=user_id,
            text=f"Siz hali ham {REQUIRED_CHANNEL} kanaliga a'zo bo'lmadingiz. ❌\nIltimos, oldin a'zo bo'ling va keyin qayta urunib ko'ring."
        )

# Menyu tugmalari (Kompyuter / Reyting)
async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Kompyuterga qarshi 🤖":
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
    # Inline tugma (A'zo bo'ldim) uchun handler
    app.add_handler(CallbackQueryHandler(check_sub_callback, pattern="^check_sub_"))
    # Oddiy menyu tugmalari uchun handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_buttons))
    
    app.run_polling()

if __name__ == "__main__":
    run_bot()