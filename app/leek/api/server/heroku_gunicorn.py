import os

# Bind to the port provided by Heroku
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
backlog = 2048

# Worker configuration optimized for Heroku
workers = int(os.environ.get('WEB_CONCURRENCY', 2))
worker_class = 'gevent'
worker_connections = 1000
timeout = 240
keepalive = 120

# Logging
errorlog = '-'
loglevel = os.environ.get('LEEK_API_LOG_LEVEL', 'INFO')
disable_redirect_access_to_syslog = True
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Heroku specific settings
preload_app = True
max_requests = 1000
max_requests_jitter = 100 