import os
from mongoengine import connect


class Config:
    # App Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-very-secret-key-here'

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-secret-key-here'
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour in seconds
    JWT_COOKIE_SECURE = False  # Set to True in production with HTTPS
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_CHECK_FORM = True
    JWT_COOKIE_DOMAIN = 'localhost'
    REMEMBER_COOKIE_DOMAIN = 'localhost'
    REMEMBER_COOKIE_SECURE = False

    SESSION_PROTECTION = 'strong'

    # MongoDB Configuration
    MONGODB_SETTINGS = {
        'db': 'auction_db',
        'host': 'localhost',
        'port': 27017,
        'connect': False
    }