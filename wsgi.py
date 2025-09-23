# wsgi.py
from app import create_app

# Initialize with your config
app, socketio = create_app("default")

# Expose socketio as the WSGI application for Gunicorn
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
