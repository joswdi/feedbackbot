from database_feedback.operations import get_session
from database_feedback.models import Feedback

session = get_session()
feedbacks = session.query(Feedback).all()

print(f"📊 Всего отзывов в базе: {len(feedbacks)}")
for fb in feedbacks:
    print(f"   - ID: {fb.id}, Статус: {fb.status}, Название: '{fb.title}'")

session.close()