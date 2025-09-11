import logging
from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask_jwt_extended import get_jwt_identity
from bson import ObjectId

from src.services.auction_service import AuctionService
from src.services.bid_service import BidService
from src.repositories.user_repository import UserRepository
from src.repositories.auction_repository import AuctionRepository
from src.exceptions.bid_too_low import BidTooLow

# Configure logger
logger = logging.getLogger(__name__)

bid_router = Blueprint('bid_router', __name__, url_prefix="/bid")

@bid_router.route("/place/<auction_id>", methods=["POST"])
def place_bid(auction_id):
    identity = get_jwt_identity()
    try:
        logger.info(f"Received bid request for auction_id={auction_id}, identity={identity}")

        if not identity:
            msg = "You must be logged in to place a bid"
            logger.warning("Bid attempt without login.")
            if request.is_json:
                return jsonify({"error": msg}), 401
            flash(msg, "error")
            return redirect(url_for("auth_router.login"))

        user = UserRepository.get_user_by_id(ObjectId(identity))
        if not user:
            msg = "User not found"
            logger.error(f"No user found with id={identity}")
            if request.is_json:
                return jsonify({"error": msg}), 404
            flash(msg, "error")
            return redirect(url_for("auction_router.list_auctions"))

        auction = AuctionRepository.get_auction_by_id(ObjectId(auction_id))
        if not auction:
            msg = "Auction not found"
            logger.error(f"No auction found with id={auction_id}")
            if request.is_json:
                return jsonify({"error": msg}), 404
            flash(msg, "error")
            return redirect(url_for("auction_router.list_auctions"))


        # Handle both form and JSON bid submissions
        if request.is_json:
            bid_amount = float(request.json.get("bid_amount"))
        else:
            bid_amount = float(request.form.get("bid_amount"))

        logger.info(f"User {user.username} ({user.id}) placing bid: {bid_amount} on auction {auction.id}")

        BidService.place_bid(auction.id, user.id, bid_amount)
        logger.info(f"User {user.username} ({user.id}) placed bid: {bid_amount} on auction {auction.id} successfully.")
        # Update current bid on auction
        updated_auction = AuctionService.update_current_bid(ObjectId(auction.id), bid_amount)
        if updated_auction:
            logger.info(f"Updated auction current bid: {updated_auction.current_bid}")
        else:
            logger.error(f"Failed to update current bid for auction={auction.id}")

        msg = "Bid placed successfully!"
        if request.is_json:
            return jsonify({
                "message": msg,
                "auction_id": str(auction.id),
                "new_current_bid": updated_auction.current_bid if updated_auction else bid_amount
            }), 200

        flash(msg, "success")

        return redirect(url_for("auction_router.auction_detail", auction_id=auction.id))

    except BidTooLow:
        msg = "Your bid must be higher than the current bid"
        logger.warning(f"Bid too low: auction={auction_id}, bidder={identity}")
        if request.is_json:
            return jsonify({"error": msg}), 400
        flash(msg, "error")
        return redirect(url_for("auction_router.auction_detail", auction_id=auction_id))
    except Exception as e:
        msg = "Exception Error"
        logger.warning(f"Caught an exception: auction={auction_id}, bidder={identity} with {e}")
        if request.is_json:
            return jsonify({"error": {e}}), 400
        flash(msg, "error")
        return redirect(url_for("auction_router.auction_detail", auction_id=auction_id))
