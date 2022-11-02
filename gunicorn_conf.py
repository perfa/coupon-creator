import multiprocessing

cores = multiprocessing.cpu_count()
workers_per_core = 2.0
default_web_concurrency = workers_per_core * cores
web_concurrency = int(default_web_concurrency)

# Gunicorn config variables
loglevel = 'info'
errorlog = '-'  # stderr
accesslog = '-'  # stdout
worker_tmp_dir = '/dev/shm'
graceful_timeout = 120
timeout = 120
keepalive = 5
workers = web_concurrency
threads = 3
