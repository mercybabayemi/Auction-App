from datetime import datetime

from src.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash

class UserRepository:
    @staticmethod
    def create_user(username, email, password, first_name=None, last_name=None):
        hashed_password = generate_password_hash(password)
        user = User(
            username=username,
            password=hashed_password,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.save()
        return user

    @staticmethod
    def find_by_username(username):
        return User.objects(username=username).first()

    @staticmethod
    def find_by_email(email):
        return User.objects(email=email).first()

    @staticmethod
    def verify_password(user, password):
        print(f"Comparing password hash for user: {user}")
        result = check_password_hash(user.password, password)
        print(f"Password matched after checking password")
        return result

    @staticmethod
    def get_user_by_id(user_id):
        return User.objects.get(id=user_id)

    @staticmethod
    def get_active_users():
        return User.objects(is_active=True).all()

    @staticmethod
    def get_active_user_by_id(user_id):
        return User.objects(id=user_id, is_active=True).first()

    @staticmethod
    def update_user_names(user_id, **updated_data):
        update_fields = {}
        for key, value in updated_data.items():
            if value is not None:
                update_fields[key] = value

        if update_fields:
            update_fields["updated_at"] = datetime.utcnow()
            return User.objects(id=user_id).update(**update_fields)

    @staticmethod
    def update_user_status(user_id, is_active):
        print(f"Updating user {user_id} to is_active={is_active}")
        result = User.objects(id=user_id).update(
            is_active=is_active,
            updated_at=datetime.utcnow()
        )
        print(f"Update result: {result}")  # Should return 1 if successful
        return result