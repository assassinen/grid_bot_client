from flask import Flask, render_template
import time
from celery_utils import get_celery_app_instance

app = Flask(__name__)
celery = get_celery_app_instance(app)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# route that will show will simply render an HTML template
@app.route("/tasks")
def tasks():
    return render_template("tasks.html")

# route that will execute a long-running task
@app.route("/long_running_task")
def long_running_task():
    # time in seconds
    time_to_wait = 15
    print(f"This task will take {time_to_wait} seconds to complete...")
    time.sleep(time_to_wait)
    return f"<p>The task completed in {time_to_wait} seconds!"

@app.route("/long_running_task_celery")
def long_running_task_celery():
    # function.delay() is used to trigger function as celery task
    sending_email_with_celery.delay()
    return f"Long running task triggered with Celery! Check terminal to see the logs..."

@celery.task
def sending_email_with_celery():
    print("Executing Long running task : Sending email with celery...")
    time.sleep(15)
    print("Task complete!")

# CELERY_TASK_LIST = [
#     'main.tasks'
# ]
#
# def make_celery():
#     celery = Celery(
#         backend=app.config['CELERY_BROKER_URL'],
#         broker=app.config['CELERY_BROKER_URL'],
#         include=CELERY_TASK_LIST
#         # backend=CELERY_BROKER_URL,
#         # broker=CELERY_BROKER_URL
#     )
#
#     class ContextTask(celery.Task):
#         abstract = True
#
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return self.run(*args, **kwargs)
#     celery.Task = ContextTask
#     return celery
#
#
# @app.route("/main")
# def async_job():
#     pass