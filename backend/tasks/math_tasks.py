from backend.celery_app import celery

@celery.task(name='tasks.add_numbers')
def add_numbers(x, y):
    return x + y
