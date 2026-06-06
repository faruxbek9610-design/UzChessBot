from sqlalchemy import create_engine, Column, BigInteger, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ma'lumotlar bazasi fayli (Hozircha oson bo'lishi uchun SQLite'dan foydalanamiz)
DATABASE_URL = "sqlite:///./chess_bot.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 1. Foydalanuvchilar daftari (User modeli)
class User(Base):
    __tablename__ = "users"

    telegram_id = Column(BigInteger, primary_key=True, index=True) # Telegram raqami
    username = Column(String, nullable=True)                      #@username
    elo_rating = Column(Integer, default=1200)                    # Shaxmat reytingi
    coins = Column(Integer, default=100)                          # Bepul tangalar
    wins = Column(Integer, default=0)                             # Yutuqlar soni
    losses = Column(Integer, default=0)                           # Mag'lubiyatlar soni

# Daftarlarni (jadvallarni) yaratish uchun funksiya
def init_db():
    Base.metadata.create_all(bind=engine)
    from sqlalchemy import ForeignKey

# 2. O'yinlar daftari (Game modeli)
class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    white_player = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=True) # Oqlar (Link yaratgan odam bo'lishi mumkin)
    black_player = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=True) # Qoralar (Linkka birinchi kirgan odam)
    
    # O'yin sozlamalari
    time_limit = Column(Integer, default=300)   # O'yin vaqti soniyalarda (masalan, 5 daqiqa = 300 soniya)
    chosen_color = Column(String, default="random") # Link yaratuvchi tanlagan rang ("white", "black" yoki "random")
    
    # O'yin holati va tarixi
    status = Column(String, default="waiting")  # "waiting" (kutmoqda), "playing" (o'ynalmoqda), "finished" (tugadi)
    moves_history = Column(String, default="")  # Yurishlar matni (masalan: "e2e4 e7e5 g1f3")
    winner_id = Column(BigInteger, nullable=True) # G'olib bo'lgan o'yinchining Telegram ID raqami
    # 3. Guruhlar daftari (Group modeli)
class Group(Base):
    __tablename__ = "groups"

    group_id = Column(BigInteger, primary_key=True, index=True) # Guruhning Telegram ID raqami
    group_name = Column(String, nullable=False)                 # Guruh nomi
    is_active = Column(Integer, default=1)                      # Bot guruhda faolmi (1) yoki chiqarib yuborilganmi (0)