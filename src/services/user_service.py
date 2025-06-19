from src.exceptions.unauthorized_access import UnauthorizedAccess
from src.exceptions.user_does_not_exists import UserDoesNotExist
from src.repositories.user_repository import UserRepository
from src.exceptions.user_already_exists import UserAlreadyExists
from src.exceptions.invalid_credentials import InvalidCredentials

class UserService:
    @staticmethod
    def register_user(username, email, password, first_name=None, last_name=None):
        if UserRepository.find_by_username(username):
            raise UserAlreadyExists(f"Username '{username}' already exists")
        if UserRepository.find_by_email(email):
            raise UserAlreadyExists(f"Email '{email}' already exists")
        return UserRepository.create_user(username, email, password, first_name=first_name, last_name=last_name)

    @staticmethod
    def login_user(username, password):
        user = UserRepository.find_by_username(username)
        if not user or not UserRepository.verify_password(user, password):
            raise InvalidCredentials("Invalid username or password")
        return user

    @staticmethod
    def delete_user(user_id):
        user = UserRepository.get_user_by_id(user_id)
        if not user:
            raise UnauthorizedAccess("User is not authorized to perform this action.")
        UserRepository.update_user_status(user_id, is_active=False)

    @staticmethod
    def edit_profile(user_id, first_name, last_name):
        user = UserRepository.get_user_by_id(user_id)
        print(f"Editing profile for {user}")
        if not user:
            raise UserDoesNotExist("User not found")
        UserRepository.update_user_names(user_id, first_name, last_name)
