import os
from celery import Celery

# 设置默认Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ModelChain.settings')

# 创建Celery实例
app = Celery('opencompass')

# 使用Django的settings文件配置Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 配置额外设置
app.conf.update(
    task_track_started=True,
    task_time_limit=30 * 60,
    broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=1
)

# 自动发现任务
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


