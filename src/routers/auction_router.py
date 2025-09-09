# src/routers/auction_router.py
"""
Router / Controller layer for auctions.
 - Keeps request parsing and response formatting responsibilities
 - Delegates business logic to AuctionService
 - Uses JWT for protected actions
"""
import logging
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

from src.repositories.auction_repository import AuctionRepository
from src.repositories.user_repository import UserRepository
from src.services.auction_service import AuctionService
from src.services.bid_service import BidService

logger = logging.getLogger(__name__)

auction_router = Blueprint('auction_router', __name__, url_prefix='/auction')


@auction_router.route('/create', methods=['GET', 'POST'])
@jwt_required(optional=True)  # allow viewing form without auth, but require auth for POST processing
def create_auction():
    """
    Handles:
     - GET => render create.html
     - POST (form-data from HTML) => create auction using form fields (image_urls hidden inputs OR files)
     - POST (application/json) => create auction from JSON (image_urls in JSON)
    """
    if request.method == 'GET':
        return render_template('auction/create.html')

    # POST
    try:
        # If incoming request is JSON (e.g., from fetch), parse JSON
        payload = {}
        if request.is_json:
            payload = request.get_json()
            logger.debug("Received JSON payload for create_auction")
        else:
            # Otherwise, assemble payload from form fields
            # Collect image_urls hidden inputs (one per secure URL)
            form = request.form
            payload['item_title'] = form.get('item_title')
            payload['item_description'] = form.get('item_description')
            payload['starting_bid'] = form.get('starting_bid')
            payload['end_time'] = form.get('end_time')
            payload['item_condition'] = form.get('item_condition')
            payload['category'] = form.get('category')
            # image_urls from hidden inputs added by frontend (one per url)
            image_urls = request.form.getlist('image_urls')
            if image_urls:
                payload['image_urls'] = image_urls
            # files fallback (if the frontend didn't upload to Cloudinary)
            files = request.files.getlist('images')
            if files and any(f.filename for f in files):
                payload['images'] = files

        # Enforce authentication for creation (create requires a logged-in user)
        identity = get_jwt_identity()
        if not identity:
            logger.warning("Unauthenticated attempt to create auction")
            flash('You must be logged in to create an auction', 'error')
            return redirect(url_for('auth_router.login'))

        # Delegate to service (which will do validations)
        auction = AuctionService.create_auction(payload, seller_id=identity)

        # If request is JSON, return JSON response
        if request.is_json:
            return jsonify(auction.to_dict()), 201

        # For form submission, redirect to the auction detail page
        flash('Auction created successfully!', 'success')
        return redirect(url_for('auction_router.auction_detail', auction_id=str(auction.id)))

    except PermissionError as pe:
        logger.warning(f"Permission error creating auction: {pe}")
        if request.is_json:
            return jsonify({'error': str(pe)}), 403
        flash(str(pe), 'error')
        return redirect(url_for('auction_router.create_auction'))
    except ValueError as ve:
        logger.warning(f"Validation error creating auction: {ve}")
        if request.is_json:
            return jsonify({'error': str(ve)}), 400
        flash(str(ve), 'error')
        return redirect(url_for('auction_router.create_auction'))
    except Exception as e:
        logger.exception(f"Unexpected error creating auction: {e}")
        if request.is_json:
            return jsonify({'error': 'Internal server error'}), 500
        flash('An unexpected error occurred', 'error')
        return redirect(url_for('auction_router.create_auction'))


@auction_router.route('/')
def list_auctions():
    try:
        search_query = request.args.get('search', '').strip()
        category = request.args.get('category')
        auctions = AuctionService.search_auctions(search_query=search_query, category=category)
        # Render HTML page (legacy)
        return render_template("auction.html",auctions=auctions, categories=['Electronics','Fashion','Home','Collectibles','Other'], selected_category=category, search_query=search_query)
    except Exception as e:
        logger.exception(f"Error listing auctions as {e}")
        flash('Failed to load list auctions', 'error')
        return redirect(url_for('user_router.index'))


@auction_router.route('/<auction_id>')
def auction_detail(auction_id):
    try:
        print("Accessing auction detail")
        auction = AuctionService.get_auction_by_id(auction_id)
        if not auction:
            flash('Auction not found', 'error')
            return redirect(url_for('auction_router.list_auctions'))
        # Get bids via BidService
        # Render detail template
        #But first is to resolve logged-in user JWT
        identity = get_jwt_identity()
        user = None
        if identity and ObjectId.is_valid(identity):
            user = UserRepository.get_user_by_id(ObjectId(identity))

        #fetch auction bids
        bids = BidService.get_bids_for_auction(ObjectId(auction_id))
        return render_template('auction/detail.html', auction=auction, bids=bids, current_time=datetime.utcnow(), current_user=user)
    except Exception as e:
        logger.exception(f"Error retrieving auction {auction_id}")
        flash('Error loading auction', 'error')
        return redirect(url_for('auction_router.list_auctions'))


@auction_router.route('/<auction_id>/delete', methods=['POST','DELETE'])
@jwt_required()
def delete_auction(auction_id):
    try:
        identity = get_jwt_identity()
        AuctionService.delete_auction(auction_id, current_user_id=identity)
        flash('Auction deleted successfully', 'success')
        return redirect(url_for('auction_router.list_auctions'))
    except PermissionError as pe:
        logger.warning(f"Unauthorized delete attempt: {pe}")
        flash(str(pe), 'error')
        return redirect(url_for('auction_router.auction_detail', auction_id=auction_id))
    except Exception as e:
        logger.exception(f"Error deleting auction {auction_id}")
        flash('An error occurred while deleting the auction', 'error')
        return redirect(url_for('auction_router.auction_detail', auction_id=auction_id))
