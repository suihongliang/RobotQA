# -*- coding: utf-8 -*-

# author: shawn

from multiprocessing import cpu_count


def max_workers():
    """get worker"""
    return cpu_count()


bind = '127.0.0.1:8080'

workers = max_workers()
worker_class = 'sync'
worker_connections = 1000
timeout = 50
max_requests = 2000

loglevel = 'info'


accesslog = '/home/ubuntu/logs/gunicorn_access.log'
errorlog = '/home/ubuntu/logs/gunicorn_err.log'
