import eventlet
eventlet.monkey_patch()

import logging
from datetime import datetime

import redis
from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from flask_mongoengine import MongoEngine
from flask_session import Session
from flask_socketio import SocketIO
from flasgger import Swagger
from mongoengine import disconnect

from config import config_by_name
from src.exceptions.user_does_not_exists import UserDoesNotExist
from src.models.user import User
from src.repositories.auction_repository import AuctionRepository
from src.routers.user_router import user_router
from src.routers.auth_router import auth_router
from src.routers.auction_router import auction_router
from src.routers.bid_router import bid_router
from src.routers.socket_events import register_socketio_events
from src.services.auction_service import AuctionService

# Load .env file early
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # switch to DEBUG for more details
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Global Redis client (populated in create_app)
redis_client = None


def create_app(config_name: str = "default"):
    my_app = Flask(__name__, instance_relative_config=True)
    my_app.config.from_object(config_by_name[config_name])

    # ----------------------------
    # Redis setup
    # ----------------------------
    redis_url = my_app.config["REDIS_URL"]
    global redis_client
    redis_client = redis.from_url(redis_url)

    # Session backend on Redis
    my_app.config["SESSION_TYPE"] = "redis"
    my_app.config["SESSION_REDIS"] = redis.from_url(redis_url)
    Session(my_app)

    # Test connection
    try:
        redis_client.ping()
        logger.info(f"✅ Connected to Redis at {redis_url}")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")

    my_app.extensions["redis"] = redis_client

    # ----------------------------
    # Database setup
    # ----------------------------
    if config_name == "testing":
        disconnect(alias="testdb")

    MongoEngine(my_app)
    jwt = JWTManager(my_app)

    # ----------------------------
    # Socket.IO setup
    # ----------------------------
    socketio = SocketIO(
        my_app,
        cors_allowed_origins="*",
        async_mode="eventlet",
        logger=True,
        engineio_logger=True,
        message_queue=redis_url
    )
    register_socketio_events(socketio)

    # ----------------------------
    # JWT callbacks
    # ----------------------------
    @jwt.user_identity_loader
    def user_identity_loader(user):
        logger.debug(f"Identity loader received: {user} (type={type(user)})")
        return user if user else None

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        try:
            identity = ObjectId(jwt_data["sub"])
            logger.info(f"User lookup for: {identity}")
            return User.objects.get(id=identity)
        except Exception as e:
            logger.warning(f"User lookup failed: {e}")
            return None

    # ----------------------------
    # Middleware / hooks
    # ----------------------------
    @my_app.before_request
    def log_cookies_and_jwt():
        logger.info("=== Incoming Request ===")
        logger.debug(f"Cookies: {request.cookies}")
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            logger.info(f"JWT Identity: {identity}")
        except Exception as e:
            logger.error(f"JWT verification failed: {e}")

    # ----------------------------
    # Template filters
    # ----------------------------
    @my_app.template_filter("datetimeformat")
    def datetimeformat(value, fmt: str = "%Y-%m-%d %H:%M"):
        return "" if value is None else value.strftime(fmt)

    @my_app.template_filter("is_active_user")
    def is_active_user(user):
        return user and getattr(user, "is_active", False)

    @my_app.template_filter("cld_thumb")
    def cld_thumb(url, width=400, height=300, crop="fill", quality="auto", fmt="auto"):
        """Transform a Cloudinary URL for thumbnails."""
        if not url or "/upload/" not in url:
            return url
        transformation = f"/upload/w_{width},h_{height},c_{crop},q_{quality},f_{fmt}/"
        return url.replace("/upload/", transformation)

    # ----------------------------
    # Template context processors
    # ----------------------------
    @my_app.context_processor
    def inject_common_context():
        def is_authenticated():
            try:
                verify_jwt_in_request(optional=True)
                return bool(get_jwt_identity())
            except Exception:
                return False

        def get_current_user():
            try:
                verify_jwt_in_request(optional=True)
                if user_id := get_jwt_identity():
                    return User.objects.get(id=ObjectId(user_id))
            except Exception as e:
                logger.error(f"User lookup failed: {e}")
            return None

        return dict(
            datetime=datetime,
            is_authenticated=is_authenticated,
            current_user=get_current_user,
            AuctionRepository=AuctionRepository,
            config=my_app.config,
        )

    # ----------------------------
    # Blueprints
    # ----------------------------
    with my_app.app_context():
        my_app.register_blueprint(user_router, url_prefix="/user")
        my_app.register_blueprint(auth_router, url_prefix="/auth")
        my_app.register_blueprint(auction_router, url_prefix="/auction")
        my_app.register_blueprint(bid_router, url_prefix="/bid")

    # ----------------------------
    # Routes
    # ----------------------------
    @my_app.route("/")
    def index():
        featured_auctions = AuctionService.get_featured_auctions(limit=20)
        return render_template("index.html", featured_auctions=featured_auctions)

    # ----------------------------
    # Error handlers
    # ----------------------------
    @my_app.errorhandler(404)
    def page_not_found(e):
        logger.warning("404 Not Found")
        return render_template("404.html"), 404

    @my_app.errorhandler(403)
    def forbidden(e):
        logger.warning("403 Forbidden")
        return render_template("403.html"), 403

    @my_app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"500 Internal Server Error: {e}")
        return render_template("500.html"), 500

    # ----------------------------
    # Swagger API docs
    # ----------------------------
    Swagger(app=my_app)

    # Redis smoke test
    redis_client.set("foo", "bar")
    logger.info(f"Redis test key foo={redis_client.get('foo')}")

    return my_app, socketio


if __name__ == "__main__":
    app, socketio = create_app("default")
    logger.info("Starting AuctionApp...")
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
