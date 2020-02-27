from __future__ import absolute_import
from celery import Celery
from datetime import timedelta

app = Celery("celery_task")
app.config_from_object("celery_task.celery_config")

app.conf.timezone = "Asia/Shanghai"
app.conf.enable_utc = False

