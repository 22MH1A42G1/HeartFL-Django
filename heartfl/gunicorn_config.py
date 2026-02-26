# ============================================================================
# GUNICORN CONFIGURATION FOR HEARTFL PRODUCTION
# ============================================================================
# Usage: gunicorn -c gunicorn_config.py heartfl.wsgi
# Or as a systemd service - see deployment guide
# ============================================================================

import multiprocessing
import os

# Server socket binding
bind = os.environ.get('GUNICORN_BIND', '127.0.0.1:8000')
backlog = 2048

# Worker processes
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count()))
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
accesslog = os.environ.get('GUNICORN_ACCESS_LOG', '/var/log/heartfl/access.log')
errorlog = os.environ.get('GUNICORN_ERROR_LOG', '/var/log/heartfl/error.log')
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'heartfl'

# Server hooks
def post_fork(server, worker):
    """Handle configuration after fork"""
    pass

def pre_fork(server, worker):
    """Handle configuration before fork"""
    pass

def pre_exec(server):
    """Handle configuration before exec"""
    pass

def when_ready(server):
    """Handle when server is ready"""
    print("🚀 Gunicorn server is ready. Spawning workers")

def worker_int(worker):
    """Handle SIGTERM"""
    pass

def worker_abort(worker):
    """Handle SIGABRT"""
    pass

# Django settings
raw_env = ['DJANGO_SETTINGS_MODULE=heartfl.settings']
