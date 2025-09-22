import os


class Config:
    # App Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')

    # Cloudinary configuration
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

    # Image upload settings
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    CLOUDINARY_UPLOAD_FOLDER = 'auction_app/images'
    CLOUDINARY_UNSIGNED_PRESET = 'auction_unsigned_preset'

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    JWT_COOKIE_SECURE = False  # Set to True in production
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_COOKIE_DOMAIN = None
    JWT_COOKIE_PATH = '/'
    JWT_SESSION_COOKIE = True

    # Disable CSRF for simplicity (enable in production)
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_CSRF_CHECK_FORM = False

    # Redis Configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # MongoDB Configuration
    # Use Atlas URI if provided, otherwise fallback to local
    MONGODB_SETTINGS = {
        'db': os.getenv('MONGODB_DATABASE', 'auction_db'),
        'host': os.getenv('MONGO_URI', 'mongodb://localhost:27017/auction_db'),
        'alias': 'default',
        'connect': False
    }


class TestingConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    JWT_SECRET_KEY = "test-jwt-secret"
    MONGODB_SETTINGS = {
        "db": "mongoenginetest",
        "alias": "testdb",
        "host": "mongodb://localhost"
    }


# Mapping
config_by_name = {
    "default": Config,
    "testing": TestingConfig,
}