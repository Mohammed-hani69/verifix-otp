#!/usr/bin/env python3
"""
إعدادات Gunicorn لتطبيق Email Sender Pro
ملف إعدادات خادم الويب للإنتاج
"""

import multiprocessing
import os

# معلومات الخادم
bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# إعدادات الأمان
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# إعدادات التسجيل
accesslog = "/var/log/email_sender/access.log"
errorlog = "/var/log/email_sender/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# معالجة الإشارات
graceful_timeout = 120
user = "www-data"
group = "www-data"

# إعدادات SSL (إذا كان مطلوباً)
# keyfile = "/path/to/ssl/private.key"
# certfile = "/path/to/ssl/certificate.crt"

def when_ready(server):
    """دالة تنفذ عند جاهزية الخادم"""
    server.log.info("Email Sender Pro Server is ready. Listening on: %s", server.address)

def worker_int(worker):
    """دالة معالجة مقاطعة العامل"""
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    """دالة تنفذ قبل تشعب العامل"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """دالة تنفذ بعد تشعب العامل"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_abort(worker):
    """دالة معالجة إلغاء العامل"""
    worker.log.info("worker received SIGABRT signal")
