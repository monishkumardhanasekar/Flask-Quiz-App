"""
Celery Worker - Run this to process saga tasks
Usage: celery -A celery_worker.celery worker --loglevel=info
"""
from app.celery_app import celery

# Import tasks and sagas to register them with Celery
from app.tasks import saga_tasks
from app.sagas import user_registration_saga

if __name__ == '__main__':
    celery.start()

