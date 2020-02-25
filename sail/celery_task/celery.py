from __future__ import absolute_import
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

app = Celery("beat-task")
app.config_from_object("app.celery_config")

app.conf.timezone = "Asia/Shanghai"
app.conf.enable_utc = False

app.conf.beat_schedule = {
    "stock_pool_update":{
        "task":"celery_tasks.tasks.stock_pool_update",
        "schedule":crontab(minute=1,hour=24),
    },
}


