import os

bind = os.getenv("BIND", "0.0.0.0:5003")
workers = int(os.getenv("WEB_CONCURRENCY", "1"))
threads = int(os.getenv("GUNICORN_THREADS", "2"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "300"))
accesslog = "-"
errorlog = "-"
