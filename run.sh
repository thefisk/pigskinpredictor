#!/bin/sh
set -e
gunicorn djangosite01.wsgi --log-file -