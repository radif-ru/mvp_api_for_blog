#!/bin/sh

# Gunicorn используется для связи Django-проекта и Nginx
gunicorn config.wsgi:application -b 0.0.0.0:3333 --reload
