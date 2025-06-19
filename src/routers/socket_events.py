from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_socketio import emit
from src.models.user import User
from src.services.auction_service import AuctionService
from src.services.bid_service import BidService
from datetime import datetime

def register_socketio_events(socketio):
    @socketio.on('place_bid')
    def handle_place_bid(data):
        try:
            # Verify JWT and get user identity
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                if not user_id:
                    emit('bid_error', {'message': 'Authentication required'})
                    return
                user = User.objects.get(id=user_id)
            except Exception as e:
                emit('bid_error', {'message': 'Authentication failed'})
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
                bidder_id=user.id,
                bid_amount=bid_amount
            )

            # Broadcast updates
            emit('new_bid', {
                'auction_id': auction_id,
                'bid_amount': bid_amount,
                'bidder_id': str(user.id),
                'bidder_name': user.username,
                'timestamp': bid.created_at.isoformat()
            }, broadcast=True)

            emit('update_price', {
                'auction_id': auction_id,
                'current_price': bid_amount
            }, broadcast=True)

        except Exception as e:
            emit('bid_error', {'message': str(e)})