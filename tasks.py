import celery
app = celery.Celery('example')

CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
app.conf.update(BROKER_URL=CELERY_BROKER_URL,
                CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND)

@app.task
def add(x, y):
    return x + y