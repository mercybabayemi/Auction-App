from bson import ObjectId
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, jsonify
from flask_jwt_extended import (
    create_access_token, set_access_cookies, unset_jwt_cookies, jwt_required, get_jwt_identity, decode_token
)

from src.exceptions.user_does_not_exists import UserDoesNotExist
from src.repositories.user_repository import UserRepository
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
            logging.info(f"User created successfully: {user}")

            if not user.is_active:
                # Create a limited-time reactivation token
                reactivate_token = create_access_token(identity=str(user.id), additional_claims={'purpose': 'reactivate'})
                logging.info(f"Reactivate token: {reactivate_token}")
                flash('Your account is deactivated. Please reactivate it.', 'warning')
                return redirect(url_for('auth_router.reactivate', token= reactivate_token, _external=False))

            access_token = create_access_token(identity=str(user.id))
            response = make_response(redirect(url_for('auction_router.list_auctions')))
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

@auth_router.route('/reactivate', methods=['GET', 'POST'])
def reactivate():
    token = request.args.get('token')
    print(f"Gotten token{token}")
    user = None
    user_id = None

    if token:
        try:
            #verify the reactivation token
            decoded = decode_token(token)
            print(f"Decoded token is {decoded}")
            if decoded.get('purpose') != 'reactivate':
                flash('Invalid reactivation because you do not need to reactivate', 'error')
                return redirect(url_for('auth_router.login'))
            user_id = ObjectId(decoded['sub'])
            user = UserRepository.get_user_by_id(user_id)
            print(f"User is {user.username} and gotten user_id is {user_id} {type(user_id)}")
        except Exception as e:
            flash(f"Invalid or expired reactivate link: {str(e)}", 'error')
            return redirect(url_for('auth_router.login'))

        if request.method == 'POST':
            try:
                if not user: #if no token, try with username/password
                    username = request.form.get('username')
                    password = request.form.get('password')
                    user = UserRepository.find_by_username(username)
                    print(f"Gotten user is {user.username}")
                    if not user or not UserRepository.verify_password(user, password):
                        flash('Invalid credential', 'error')
                        return redirect(url_for('auth_router.reactivate'))

                if user.is_active:
                    flash('Account is already active', 'success')
                    return redirect(url_for('auth_router.login'))

                #Reactivate account
                print(f"Gotten user is {user.username}")
                UserRepository.update_user_status(user.id, True)
                flash('Account reactivated successfully! Please login', 'success')
                return redirect(url_for('auth_router.login'))

            except Exception as e:
                flash(f"Error during reactivation: {str(e)}", "error")

    return render_template('auth/reactivate.html', user = user, token = token)