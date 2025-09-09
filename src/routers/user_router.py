from bson import ObjectId
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.exceptions.invalid_credentials import InvalidCredentials
from src.exceptions.unauthorized_access import UnauthorizedAccess
from src.exceptions.user_does_not_exists import UserDoesNotExist
from src.models import user
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.auction_service import AuctionService
from src.services.bid_service import BidService
from src.services.contact_service import ContactMessageService
from src.services.user_service import UserService
import logging
logger = logging.getLogger(__name__)

user_router = Blueprint('user_router', __name__, url_prefix='/user')

@user_router.route('/protected')
@jwt_required()  # ← Auto-validates JWT
def protected():
    user_id = get_jwt_identity()
    return user_id

@user_router.route('/')
def index():
    featured_auctions = AuctionService.get_featured_auctions()
    return render_template("index.html", featured_auctions=featured_auctions)

@user_router.route('/about')
def about():
    return render_template("about.html")

@user_router.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            subject = request.form.get('subject')
            message = request.form.get('message')

            if name and email and subject and message:
                ContactMessageService.create_contact_message(name, email, subject, message)
                flash('Message sent successfully!', 'success')
                return redirect(url_for('user_router.contact'))
            else:
                flash('Please fill out all fields.', 'error')
        except Exception as e:
            flash(f"There was an error: {e}", 'error')

    return render_template("contact.html")

@user_router.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    try:
        logger.info(f"Fetching profile")
        print(f"got {type(user_id)} {user_id}")
        gotten_user = UserService.get_user_by_id(ObjectId(user_id))
        print(f"{gotten_user.username} {gotten_user.email} {gotten_user.first_name} {gotten_user.last_name}")

        user_bids = BidService.get_user_bids(ObjectId(gotten_user.id))
        print(f"User {gotten_user.username} has {len(user_bids)} bids")
        logger.info(f"User {gotten_user.username} has {len(user_bids)}")
        return render_template('profile.html', user=gotten_user, bids=user_bids)
    except UserDoesNotExist as e:
        logger.warning(f"User profile not found: {user_id}")
        flash("User does not exist.", "error")
    except UnauthorizedAccess as e:
        logger.exception("Unauthorized access")
        flash(f"UnauthorizedAccess: {e}", "error")
    except Exception as e:
        logger.exception("Error fetching user profile")
        flash(f"{e}", "error")

@user_router.route('/profile/delete', methods=['POST'])
@jwt_required()
def delete_profile():
    try:
        user_id = get_jwt_identity()
        user = UserRepository.get_user_by_id(user_id)
        if user:
            UserService.delete_user(user_id)
            flash(f'User named {str(user.username)} deleted successfully!', 'success')
            return redirect(url_for('auth_router.logout'))
    except UnauthorizedAccess as e:
        flash(f"Unauthorized access! {str(e)}", "error")
    except Exception as e:
        flash(f"Error occurred while trying to delete profile: {str(e)}")

@user_router.route('/edit_profile', methods=['POST'])
@jwt_required()
def edit_profile():
    gotten_id = get_jwt_identity()
    user_id = ObjectId(gotten_id)
    gotten_user = UserRepository.get_user_by_id(user_id)
    try:
        if gotten_user:
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            UserService.edit_profile(user_id, first_name, last_name)
            logger.info(f"User edited {first_name} {last_name}")
            flash(f"Profile updated successfully!", "success")

            user_bids = BidService.get_user_bids(ObjectId(gotten_user.id))

            logger.info(f"User {gotten_user.username} has {len(user_bids)}")

            return redirect(url_for('user_router.profile'))
    except UserDoesNotExist as e:
        logger.warning("Delete user attempted for user not found")
        flash("User does not exist.", "error")
    except Exception as e:
        flash(f"Error occurred while trying to edit profile: {str(e)}")
    return render_template("profile.html", user=user)