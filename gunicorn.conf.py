# gunicorn.conf.py
import os

# Configurações básicas
bind = f"0.0.0.0:{os.environ.get('PORT', 10000)}"
workers = 1  # Apenas 1 worker para economizar memória
worker_class = "sync"

# Timeouts aumentados para APIs lentas
timeout = 120  # 2 minutos (padrão era 30s)
keepalive = 5
max_requests = 100
max_requests_jitter = 10

# Configurações de memória
worker_memory_limit = 512 * 1024 * 1024  # 512MB por worker
preload_app = True  # Carrega a aplicação antes de fazer fork

# Logs
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações de processo
user = None
group = None
tmp_upload_dir = None
secure_scheme_headers = {
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}