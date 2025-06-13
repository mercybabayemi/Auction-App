from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, jsonify
from flask_jwt_extended import (
create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
)
from flask_login import current_user, login_user, logout_user
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
    if current_user.is_authenticated:
        return redirect(url_for('user_router.auction'))

    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')

            user = UserService.login_user(username, password)

            access_token = create_access_token(identity=str(user.id))
            response = make_response(redirect(url_for('user_router.auction')))
            set_access_cookies(response, access_token)

            login_user(user)

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
    logout_user()
    flash('Logged out successfully!', 'success')
    return response

@auth_router.route('/protected')
@jwt_required
def protected():
    current_user_id = get_jwt_identity()
    return jsonify(logged_in_as=current_user_id), 200