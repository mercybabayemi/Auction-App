import logging
from src.exceptions.unauthorized_access import UnauthorizedAccess
from src.exceptions.user_does_not_exists import UserDoesNotExist
from src.repositories.user_repository import UserRepository
from src.exceptions.user_already_exists import UserAlreadyExists
from src.exceptions.invalid_credentials import InvalidCredentials
logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    def register_user(username, email, password, first_name=None, last_name=None):
        logger.info(f"Registering user: {username}, email={email}")
        if UserRepository.find_by_username(username):
            logger.warning(f"User already exists: {username}")
            raise UserAlreadyExists(f"Username '{username}' already exists")
        if UserRepository.find_by_email(email):
            logger.warning(f"User already exists: {email}")
            raise UserAlreadyExists(f"Email '{email}' already exists")
        return UserRepository.create_user(username, email, password, first_name=first_name, last_name=last_name)

    @staticmethod
    def login_user(username, password):
        logger.info(f"Login attempt: {username}")
        user = UserRepository.find_by_username(username)
        if not user or not UserRepository.verify_password(user, password):
            logger.warning(f"Login failed: user not found {username}, Login failed: invalid password for {username}")
            raise InvalidCredentials("Invalid username or password")
        logger.info(f"Login success: {username}")
        return user

    @staticmethod
    def delete_user(user_id):
        logger.info(f"Deleting user {user_id}")
        user = UserRepository.get_user_by_id(user_id)
        if not user:
            logger.warning(f"User not found for delete: {user_id}")
            raise UnauthorizedAccess("User is not authorized to perform this action.")
        UserRepository.update_user_status(user_id, is_active=False)

    @staticmethod
    def edit_profile(user_id, first_name, last_name):
        logger.info(f"Editing user {user_id}")
        user = UserRepository.get_user_by_id(user_id)
        print(f"Editing profile for {user}")
        if not user:
            raise UserDoesNotExist("User not found")
        update_data = {}
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name
        UserRepository.update_user(user_id, **update_data)

    @staticmethod
    def get_user_by_id(user_id):
        logger.debug(f"Fetching user {user_id}")
        return UserRepository.get_user_by_id(user_id)
