import os


class Config:
    # App Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-very-secret-key-here'

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-secret-key-here'
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    JWT_COOKIE_SECURE = False  # True in production
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_COOKIE_DOMAIN = None
    JWT_COOKIE_PATH = '/'
    JWT_SESSION_COOKIE = True


    # Disable CSRF for simplicity (enable in production)
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_CSRF_CHECK_FORM = False

    # MongoDB Configuration
    MONGODB_SETTINGS = {
        'db': 'auction_db',
        'host': 'localhost',
        'port': 27017,
        'connect': False
    }