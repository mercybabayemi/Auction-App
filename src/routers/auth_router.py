from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, jsonify
from flask_jwt_extended import (
create_access_token, set_access_cookies, unset_jwt_cookies
)
from src.services.user_service import UserService
from src.exceptions.user_already_exists import UserAlreadyExists
from src.exceptions.invalid_credentials import InvalidCredentials

auth_router = Blueprint('auth_router', __name__, url_prefix='/auth')

@auth_router.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')

            user = UserService.register_user(username, email, password, first_name, last_name)
            print(str(user.to_dict()))
            print("User id is " + str(user.id))

            access_token = create_access_token(identity=str(user.id))
            response = make_response(redirect(url_for('auth_router.login')))
            set_access_cookies(response, access_token)
            flash('Registration successful! Please log in to continue.', 'success')
            return response
        except InvalidCredentials as e:
            flash(str(e), 'error')
        except UserAlreadyExists as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred during registration' + str(e), 'error')

    return render_template('auth/register.html')

@auth_router.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            print(f"Attempting login for username: {username}")
            user = UserService.login_user(username, password)
            print(f"User found: {user.username}, ID: {user.id}")
            access_token = create_access_token(identity=str(user.id))
            response = make_response(redirect(url_for('user_router.auction')))
            set_access_cookies(response, access_token)
            print(f"Current user after login is {username}")
            flash('Login successful!', 'success')
            return response
        except InvalidCredentials as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred during login', 'error')

    return render_template('auth/login.html')


@auth_router.route('/logout', methods=['GET'])
def logout():
    response = make_response(redirect(url_for('auth_router.login')))
    unset_jwt_cookies(response)
    flash('Logged out successfully!', 'success')
    return response