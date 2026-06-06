from sqlalchemy.orm import Session
from database.database import User, Game, Group

# 1. Foydalanuvchini bazaga qo'shish yoki bor bo'lsa uni qaytarish
def get_or_create_user(db: Session, telegram_id: int, username: str = None):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# 2. Foydalanuvchining reytingini (ELO) yangilash
def update_user_rating(db: Session, telegram_id: int, new_rating: int, is_win: bool):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        user.elo_rating = new_rating
        if is_win:
            user.wins += 1
        else:
            user.losses += 1
        db.commit()
        db.refresh(user)
    return user

# 3. Global eng kuchli 10 ta o'yinchi ro'yxatini olish (Leaderboard uchun)
def get_top_players(db: Session, limit: int = 10):
    return db.query(User).order_by(User.elo_rating.desc()).limit(limit).all()
# 4. Yangi o'yin havolasi (linki) uchun bazada joy ochish
def create_custom_game(db: Session, creator_id: int, time_limit: int, chosen_color: str):
    # Agar yaratuvchi oq rangni tanlasa, uni white_player ga qo'yamiz
    if chosen_color == "white":
        game = Game(white_player=creator_id, time_limit=time_limit, chosen_color=chosen_color, status="waiting")
    # Agar qora rangni tanlasa, black_player ga qo'yamiz
    elif chosen_color == "black":
        game = Game(black_player=creator_id, time_limit=time_limit, chosen_color=chosen_color, status="waiting")
    # Agar ixtiyoriy (random) tanlasa, hozircha oq rangga qo'yib turamiz (o'yin boshlanganda aniq bo'ladi)
    else:
        game = Game(white_player=creator_id, time_limit=time_limit, chosen_color=chosen_color, status="waiting")
        
    db.add(game)
    db.commit()
    db.refresh(game)
    return game

# 5. Ikkinchi o'yinchi link ustiga bosganda o'yinga ulanishi
def join_game(db: Session, game_id: int, joiner_id: int):
    game = db.query(Game).filter(Game.id == game_id, Game.status == "waiting").first()
    if game:
        # Bo'sh turgan rangga ikkinchi o'yinchini joylashtiramiz
        if game.white_player is None:
            game.white_player = joiner_id
        else:
            game.black_player = joiner_id
            
        game.status = "playing" # O'yin holatini "o'ynalyapti"ga o'zgartiramiz
        db.commit()
        db.refresh(game)
        return game
    return None # Agar o'yin topilmasa yoki allaqachon boshlanib ketgan bo'lsa