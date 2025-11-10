from sqlalchemy import func, create_engine
from sqlalchemy.orm import sessionmaker
from .models import Feedback, Base
from config import DATABASE_URL

# Добавляем функцию init_db
def init_db():
    """Инициализация базы данных"""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("✅ База данных инициализирована")
    return engine

# Создаем движок и фабрику сессий
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_session():
    """Получить сессию базы данных"""
    return SessionLocal()

def create_feedback(user_id, user_name, title, message, rating):
    """Создание нового отзыва"""
    session = get_session()
    try:
        feedback = Feedback(
            user_id=user_id,
            user_name=user_name,
            title=title,
            message=message,
            rating=rating
        )
        session.add(feedback)
        session.commit()
        session.refresh(feedback)
        return feedback
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_feedback_stats():
    """Получить статистику по отзывам"""
    session = get_session()
    try:
        total = session.query(Feedback).count()
        pending = session.query(Feedback).filter(Feedback.status == 'pending').count()
        approved = session.query(Feedback).filter(Feedback.status == 'approved').count()
        rejected = session.query(Feedback).filter(Feedback.status == 'rejected').count()
        
        # Средняя оценка только для принятых отзывов
        avg_rating_result = session.query(func.avg(Feedback.rating))\
            .filter(Feedback.status == 'approved')\
            .scalar()
        avg_rating = float(avg_rating_result) if avg_rating_result else 0.0
        
        return {
            'total': total,
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'avg_rating': round(avg_rating, 2)
        }
    finally:
        session.close()

def reset_all_feedbacks():
    """Полное удаление всех отзывов"""
    session = get_session()
    try:
        deleted_count = session.query(Feedback).delete()
        session.commit()
        return deleted_count
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def update_feedback_status(feedback_id, status, moderator_id):
    """Обновление статуса отзыва"""
    session = get_session()
    try:
        feedback = session.query(Feedback).filter(Feedback.id == feedback_id).first()
        if feedback:
            feedback.status = status
            feedback.moderated_by = moderator_id
            feedback.moderated_at = func.now()
            session.commit()
            session.refresh(feedback)
        return feedback
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_feedback(feedback_id):
    """Удаление отзыва по ID"""
    session = get_session()
    try:
        feedback = session.query(Feedback).filter(Feedback.id == feedback_id).first()
        if feedback:
            session.delete(feedback)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_feedback_by_id(feedback_id):
    """Получить отзыв по ID"""
    session = get_session()
    try:
        return session.query(Feedback).filter(Feedback.id == feedback_id).first()
    finally:
        session.close()