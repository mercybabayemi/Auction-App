from flask import Blueprint, render_template, request, flash, redirect, url_for

from src.services.auction_service import AuctionService
from src.services.contact_service import ContactMessageService
from src.services.user_service import UserService

user_router = Blueprint('user_router', __name__, url_prefix='/user')


@user_router.route('/')
def index():
    featured_auctions = AuctionService.get_featured_auctions()
    return render_template("index.html", featured_auctions=featured_auctions)

@user_router.route('/auction')
def auction():
    return render_template("auction.html")

@user_router.route('/about')
def about():
    return render_template("about.html")

@user_router.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
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

    return render_template("contact.html")
