from flask_socketio import SocketIO
from flask import Flask, render_template, request
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from flask_mongoengine import MongoEngine
from bson import ObjectId
from config import Config
from src.exceptions.user_does_not_exists import UserDoesNotExist
from src.routers.user_router import user_router
from src.routers.auth_router import auth_router
from src.routers.auction_router import auction_router
from src.routers.socket_events import register_socketio_events

socketio = SocketIO()


def create_app(test_config=None):
    my_app = Flask(__name__, instance_relative_config=True)
    my_app.config.from_object(Config)

    # Initialize extensions
    MongoEngine(my_app)
    jwt = JWTManager(my_app)
    socketio.init_app(my_app)

    # JWT configuration
    from src.models.user import User

    @jwt.user_identity_loader
    def user_identity_loader(user):
        print(f"Identity loader received: {user} (type: {type(user)})")
        return user if user else None

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        try:
            print(f"Lookup received sub: {jwt_data['sub']}")
            identity = ObjectId(jwt_data["sub"])
            return User.objects.get(id=identity)
        except (UserDoesNotExist, Exception):
            print(f"Lookup failed: {str(Exception)}")
            return None

    @my_app.before_request
    def log_cookies():
        print("\n=== Incoming Request ===")
        print("Cookies:", request.cookies)
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()

            print("JWT Identity:", identity)
        except Exception as e:
            print("JWT Verification Error:", str(e))
        print("=======================\n")

    # Template context processor
    @my_app.context_processor
    def inject_auth_status():
        def is_authenticated():
            try:
                # Verify without raising exceptions
                verify_jwt_in_request(optional=True)
                identity = get_jwt_identity()
                if identity:
                    print(f"Successful auth for user: {identity}")
                    return True
                return False
            except Exception as e:
                print(f"Auth verification failed: {e}")
                return False

        def get_current_user():
            try:
                verify_jwt_in_request(optional=True)
                if user_id := get_jwt_identity():
                    return User.objects.get(id=ObjectId(user_id))
            except Exception as e:
                print(f"User lookup failed: {e}")
            return None

        return dict(
            is_authenticated=is_authenticated,
            current_user=get_current_user
        )



    # Register blueprints
    with my_app.app_context():
        my_app.register_blueprint(user_router, url_prefix='/user')
        my_app.register_blueprint(auth_router, url_prefix='/auth')
        my_app.register_blueprint(auction_router, url_prefix='/auction')


    # Basic routes
    @my_app.route('/')
    def index():
        return render_template('index.html')

    # Error handlers
    @my_app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @my_app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @my_app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    # Socket.IO events
    register_socketio_events(socketio)

    return my_app


if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)