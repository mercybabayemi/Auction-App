# wsgi.py
from app import create_app

app, socketio = create_app("default")

# Expose the Flask app (Gunicorn needs this)
application = app   # 👈 important

if __name__ == "__main__":
    # For local debugging only
    socketio.run(app, host="0.0.0.0", port=5000)
