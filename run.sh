#!/bin/sh
set -e
gunicorn project.wsgi --log-file -