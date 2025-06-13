from flask_socketio import emit
from flask_login import current_user
from src.services.auction_service import AuctionService
from src.services.bid_service import BidService
from datetime import datetime

def register_socketio_events(socketio):
    @socketio.on('place_bid')
    def handle_place_bid(data):
        try:
            if not current_user.is_authenticated:
                emit('bid_error', {'message': 'Authentication required'})
                return

            auction_id = data['auction_id']
            bid_amount = float(data['bid_amount'])

            # Validate bid
            auction = AuctionService.get_auction_by_id(auction_id)
            if datetime.utcnow() > auction.end_time:
                emit('bid_error', {'message': 'Auction has ended'})
                return

            highest_bid = BidService.get_highest_bid(auction_id)
            if highest_bid and bid_amount <= highest_bid.bid_amount:
                emit('bid_error', {
                    'message': f'Bid must be higher than current bid (${highest_bid.bid_amount})'
                })
                return

            # Place bid
            bid = BidService.place_bid(
                auction_id=auction_id,
                bidder_id=current_user.id,
                bid_amount=bid_amount
            )

            # Broadcast updates
            emit('new_bid', {
                'auction_id': auction_id,
                'bid_amount': bid_amount,
                'bidder_id': str(current_user.id),
                'bidder_name': current_user.username,
                'timestamp': bid.created_at.isoformat()
            }, broadcast=True)

            emit('update_price', {
                'auction_id': auction_id,
                'current_price': bid_amount
            }, broadcast=True)

        except Exception as e:
            emit('bid_error', {'message': str(e)})