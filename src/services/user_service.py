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
