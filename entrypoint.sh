#!/bin/bash
set -e

echo "🚀 Starting Auction App..."

# If you want to debug, run Flask directly
# python app.py

# Otherwise run gunicorn (production mode)
exec gunicorn -k eventlet -w 1 -b 0.0.0.0:5000 wsgi:application \
    --log-level=debug \
    --capture-output \
    --enable-stdio-inheritance