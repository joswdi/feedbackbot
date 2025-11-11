from sqlalchemy import func, create_engine
from sqlalchemy.orm import sessionmaker
from .models import Report, Base
from config import DATABASE_REPORTS_URL

# Добавляем функцию init_db
def init_db():
    """Инициализация базы данных"""
    engine = create_engine(DATABASE_REPORTS_URL)
    Base.metadata.create_all(engine)
    print("✅ База данных инициализирована")
    return engine

# Создаем движок и фабрику сессий
engine = create_engine(DATABASE_REPORTS_URL)
SessionLocal = sessionmaker(bind=engine)

def get_session():
    """Получить сессию базы данных"""
    return SessionLocal()

def create_report(user_id, user_name, report_description):
    """Создание новой жалобы"""
    session = get_session()
    try:
        report = Report(
            user_id=user_id,
            user_name=user_name,
            report_discription=report_description
        )
        session.add(report)
        session.commit()
        session.refresh(report)
        return report
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_report_stats():
    """Получить статистику по жалобам"""
    session = get_session()
    try:
        total = session.query(Report).count()
        pending = session.query(Report).filter(Report.status == 'pending').count()
        approved = session.query(Report).filter(Report.status == 'approved').count()
        rejected = session.query(Report).filter(Report.status == 'rejected').count()
        
        # Средняя оценка только для принятых жалоб
        avg_rating_result = session.query(func.avg(Report.rating))\
            .filter(Report.status == 'approved')\
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

def reset_all_reports():
    """Полное удаление всех жалоб"""
    session = get_session()
    try:
        deleted_count = session.query(Report).delete()
        session.commit()
        return deleted_count
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def update_report_status(report_id, status, moderator_id):
    """Обновление статуса жалобы"""
    session = get_session()
    try:
        report = session.query(Report).filter(Report.id == report_id).first()
        if report:
            report.status = status
            report.moderated_by = moderator_id
            report.moderated_at = func.now()
            session.commit()
            session.refresh(report)
        return report
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_report(report_id):
    """Удаление жалобы по ID"""
    session = get_session()
    try:
        report = session.query(Report).filter(Report.id == report_id).first()
        if report:
            session.delete(report)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_report_by_id(report_id):
    """Получить жалобу по ID"""
    session = get_session()
    try:
        return session.query(Report).filter(Report.id == report_id).first()
    finally:
        session.close()