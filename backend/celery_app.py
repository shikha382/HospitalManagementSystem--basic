from celery import Celery
from celery.schedules import crontab
from backend.config import Config
celery = Celery(
    "hms",
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=['backend.tasks.reminders', 'backend.tasks.reports', 'backend.tasks.exports']
)
celery.conf.timezone = "Asia/Kolkata"
celery.conf.beat_schedule = {
    "send-daily-reminders": {
        "task": "tasks.send_daily_reminders",
        "schedule": crontab(minute=0)  # Every day at 8:00 AM,  
    },
    "generate-monthly-reports": {
        "task": "tasks.generate_monthly_reports",
        "schedule": crontab(minute=0)
    },
}
