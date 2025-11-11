from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Report(Base):
    __tablename__ = 'reports'
    
    # Статусы
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    target_user_id = Column(String, nullable=False)
    target_user_name = Column(String, nullable=False)
    report_description = Column(String, nullable=False)
    status = Column(String, default=PENDING)
    moderated_by = Column(String, nullable=True)
    moderated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)