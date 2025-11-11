from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE_FEEDBACK_URL

Base = declarative_base()

class Feedback(Base):
    __tablename__ = 'feedbacks'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False)
    user_name = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    status = Column(String(20), default='pending')  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    moderated_by = Column(String(50), nullable=True)
    moderated_at = Column(DateTime, nullable=True)
    
    # Статусы как константы класса
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

# Создаем engine и сессию
engine = create_engine(DATABASE_FEEDBACK_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    """Получить сессию базы данных"""
    return SessionLocal()

def init_db():
    """Инициализация базы данных - создание таблиц"""
    Base.metadata.create_all(bind=engine)
    print("✅ База данных SQLAlchemy инициализирована")