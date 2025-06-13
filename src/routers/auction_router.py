from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from flask_socketio import emit
from src.services.auction_service import AuctionService
from src.services.bid_service import BidService
from datetime import datetime
from ..exceptions.auction_not_found import AuctionNotFound
from ..repositories.auction_repository import AuctionRepository

auction_router = Blueprint('auction_router', __name__, url_prefix='/auction')


# Auction Routes
@auction_router.route('/')
def list_auctions():
    try:
        search_query = request.args.get('search', '').strip()
        category = request.args.get('category')

        auctions = AuctionService.search_auctions(
            search_query=search_query,
            category=category
        )

        categories = ['Electronics', 'Fashion', 'Home', 'Collectibles', 'Other']

        return render_template(
            'auction/list.html',
            auctions=auctions,
            categories=categories,
            selected_category=category,
            search_query=search_query
        )
    except Exception as e:
        flash('Failed to load auctions: ' + str(e), 'error')
        return redirect(url_for('user_router.auction'))

@auction_router.route('/<auction_id>')
def auction_detail(auction_id):
    try:
        auction = AuctionService.get_auction_by_id(auction_id)
        if auction is None:
            raise AuctionNotFound('Auction not found')
        bids = BidService.get_bids_for_auction(auction_id)
        return render_template('auction/detail.html',
                               auction=auction,
                               bids=bids,
                               current_time=datetime.utcnow())
    except AuctionNotFound:
        flash('Auction not found', 'error')
        return redirect(url_for('auction_router.list_auctions'))
    except Exception as e:
        flash('Error loading auction: ' + str(e), 'error')
        return redirect(url_for('auction_router.list_auctions'))


@auction_router.route('/create', methods=['GET', 'POST'])
@login_required
def create_auction():
    if request.method == 'POST':
        try:
            # Get form data
            item_title = request.form.get('item_title')
            item_description = request.form.get('item_description')
            starting_bid = float(request.form.get('starting_bid'))
            end_time = datetime.fromisoformat(request.form.get('end_time'))
            item_condition = request.form.get('item_condition')
            category = request.form.get('category')
            images = request.files.getlist('images')

            # Create auction
            auction = AuctionRepository.create_auction(
                item_title=item_title,
                item_description=item_description,
                starting_bid=starting_bid,
                end_time=end_time,
                item_condition=item_condition,
                seller=current_user._get_current_object(),
                images=images,
                category=category
            )

            flash('Auction created successfully!', 'success')
            return redirect(url_for('auction_router.auction_detail', auction_id=str(auction.id)))

        except Exception as e:
            flash(f'Error creating auction: {str(e)}', 'error')

    return render_template('auction/create.html')


# API Endpoints
@auction_router.route('/api/<auction_id>/bids', methods=['GET'])
def get_auction_bids(auction_id):
    try:
        bids = BidService.get_bids_for_auction(auction_id)
        return jsonify([{
            'bid_amount': bid.bid_amount,
            'bidder_id': str(bid.bidder_id.id),
            'timestamp': bid.created_at.isoformat()
        } for bid in bids])
    except Exception as e:
        return jsonify({'error': str(e)}), 400
