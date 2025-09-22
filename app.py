import logging
from dotenv import load_dotenv
from mongoengine import disconnect
from flasgger import Swagger
load_dotenv()  # this loads your .env file
from flask_socketio import SocketIO
from flask import Flask, render_template, request, current_app
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from flask_mongoengine import MongoEngine
from bson import ObjectId
from config import config_by_name
from src.exceptions.user_does_not_exists import UserDoesNotExist
from src.routers.user_router import user_router
from src.routers.auth_router import auth_router
from src.routers.auction_router import auction_router
from src.routers.socket_events import register_socketio_events
from src.services.auction_service import AuctionService
from src.routers.bid_router import bid_router
import redis
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.INFO,  # change to DEBUG for deeper logs
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def create_app(config_name="default"):
    my_app = Flask(__name__, instance_relative_config=True)

    my_app.config.from_object(config_by_name[config_name])

    # Redis setup
    redis_url = my_app.config["REDIS_URL"]
    redis_client = redis.from_url(redis_url)

    # Test connection once (optional but useful for Render logs)
    try:
        redis_client.ping()
        logger.info(f"Connected to Redis at {redis_url}")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")


    my_app.extensions["redis"] = redis_client

    # Disconnect existing alias if re-running in tests
    if config_name == "testing":
        disconnect(alias="testdb")

    # Initialize extensions
    MongoEngine(my_app)
    jwt = JWTManager(my_app)


    # Socket.IO events
    #cors_allowed_origins = "*", async_mode = "eventlet"
    socketio_myapp = SocketIO(my_app,
                              cors_allowed_origins="*",
                              async_mode='eventlet',
                              logger=True,
                              engineio_logger=True)
    register_socketio_events(socketio_myapp)

    # JWT configuration
    from src.models.user import User

    @jwt.user_identity_loader
    def user_identity_loader(user):
        logger.debug(f"Identity loader received: {user} (type: {type(user)})")
        return user if user else None

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        try:
            logger.info(f"Lookup received sub: {jwt_data['sub']}")
            identity = ObjectId(jwt_data["sub"])
            return User.objects.get(id=identity)
        except (UserDoesNotExist, Exception) as e:
            logger.warning(f"Lookup failed: {str(e)}")
            return None

    @my_app.before_request
    def log_cookies():
        logger.info(f"\n=== Incoming Request ===")
        logger.debug(f"Cookies:", request.cookies)
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            logger.info(f"JWT Identity:{identity}")
        except Exception as e:
            logger.error(f"JWT Verification Error:", {str(e)})

    @my_app.template_filter('datetimeformat')
    def datetimeformat(value, format='%Y-%m-%d %H:%M'):
        if value is None:
            return ""
        return value.strftime(format)

    # Template context processor
    @my_app.context_processor
    def inject_common_context():
        def is_authenticated():
            try:
                # Verify without raising exceptions
                verify_jwt_in_request(optional=True)
                identity = get_jwt_identity()
                if identity:
                    logger.debug(f"Successful auth for user: {identity}")
                    return True
                return False
            except Exception as e:
                logger.error(f"Auth verification failed: {e}")
                return False

        def get_current_user():
            try:
                verify_jwt_in_request(optional=True)
                if user_id := get_jwt_identity():
                    return User.objects.get(id=ObjectId(user_id))
            except Exception as e:
                logger.error(f"User lookup failed: {e}")
            return None
        from datetime import datetime
        from src.repositories.auction_repository import AuctionRepository
        return dict(
            datetime=datetime,
            is_authenticated=is_authenticated,
            current_user=get_current_user,
            AuctionRepository=AuctionRepository,
            config=my_app.config
        )

    logger.info(
        f"Cloudinary config - name: {my_app.config.get('CLOUDINARY_CLOUD_NAME')}, "
        f"preset: {my_app.config.get('CLOUDINARY_UNSIGNED_PRESET')}"
    )

    @my_app.template_filter('is_active_user')
    def is_active_user(user):
        return user and user.is_active

    @my_app.template_filter('cld_thumb')
    def cld_thumb(url, width=400, height=300, crop="fill", quality="auto", fmt="auto"):
        """
        Transform a Cloudinary URL with width/height/crop/quality/format.
        Example: {{ auction.image_urls[0] | cld_thumb(500, 400) }}
        """
        if not url or "/upload/" not in url:
            return url  # return untouched if invalid
        transformation = f"/upload/w_{width},h_{height},c_{crop},q_{quality},f_{fmt}/"
        return url.replace("/upload/", transformation)

    redis_client = current_app.extensions["redis"]
    redis_client.set("foo", "bar")
    print(redis_client.get("foo"))

    # Register blueprints
    with my_app.app_context():
        my_app.register_blueprint(user_router, url_prefix='/user')
        my_app.register_blueprint(auth_router, url_prefix='/auth')
        my_app.register_blueprint(auction_router, url_prefix='/auction')
        my_app.register_blueprint(bid_router, url_prefix='/bid')


    # Basic routes
    @my_app.route('/')
    def index():
        featured_auctions = AuctionService.get_featured_auctions(limit=20)
        return render_template('index.html', featured_auctions=featured_auctions)

    # Error handlers
    @my_app.errorhandler(404)
    def page_not_found(e):
        logger.warning(f"404 error encountered")
        return render_template('404.html'), 404

    @my_app.errorhandler(403)
    def forbidden(e):
        logger.warning(f"403 error encountered")
        return render_template('403.html'), 403

    @my_app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"500 error encountered: {e}")
        return render_template('500.html'), 500

    Swagger(app=my_app)

    return my_app, socketio_myapp


if __name__ == '__main__':
    app, socketio = create_app("default")
    logger.info("Starting AuctionApp...")
    socketio.run(app,
                 debug=True,
                 allow_unsafe_werkzeug=True)