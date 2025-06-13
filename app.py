from flask_socketio import SocketIO
from flask import Flask, render_template
from flask_jwt_extended import JWTManager, current_user, get_jwt_identity
from flask_login import LoginManager, login_user  # Add Flask-Login
from flask_mongoengine import MongoEngine
from bson import ObjectId
from werkzeug import security
from config import Config
from src.exceptions.user_does_not_exists import UserDoesNotExist
from src.repositories.user_repository import UserRepository
from src.routers.auction_router import auction_router
from src.routers.auth_router import auth_router
from src.routers.user_router import user_router
from src.routers.socket_events import register_socketio_events

socketio = SocketIO()
def create_app(test_config=None):
    my_app = Flask(__name__, instance_relative_config=True)

    my_app.config.from_object(Config)
    MongoEngine(my_app)

    # Initialize Flask extensions
    jwt = JWTManager(my_app)
    #my_app.jwt = jwt  # Optional: Attach JWT to app for easy access
    from src.models.user import User
    @jwt.user_identity_loader
    def user_identity_lookup(user):
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

    socketio.init_app(my_app)
    register_socketio_events(socketio)

    # 🔹 Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(my_app)

    # 🔹 User Loader (Required for Flask-Login)
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.objects.get(id=ObjectId(user_id))
        except Exception as e:
            return None  # Return None if user not found


    #THis ensures Flask-Login sees JWT login
    @my_app.before_request
    def before_request():
        if current_user.is_authenticated:
            return
        try:
            user = get_jwt_identity()
            if user:
                login_user(User.objects.get(id=ObjectId(user)))
        except:
            pass

    # Register blueprints
    with my_app.app_context():
        my_app.register_blueprint(user_router, url_prefix='/user')
        my_app.register_blueprint(auth_router, url_prefix='/auth')
        my_app.register_blueprint(auction_router, url_prefix='/auction')

    @my_app.route('/')
    def index():
        return render_template('index.html')

    #Error handler for 404
    @my_app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @my_app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @my_app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500


    return my_app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)