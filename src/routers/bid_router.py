import logging
from flask import Blueprint, request, redirect, url_for, flash
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
            flash("You must be logged in to place a bid", "error")
            logger.warning("Bid attempt without login.")
            return redirect(url_for("auth_router.login"))

        user = UserRepository.get_user_by_id(ObjectId(identity))
        if not user:
            flash("User not found", "error")
            logger.error(f"No user found with id={identity}")
            return redirect(url_for("auction_router.list_auctions"))

        auction = AuctionRepository.get_auction_by_id(ObjectId(auction_id))
        if not auction:
            flash("Auction not found", "error")
            logger.error(f"No auction found with id={auction_id}")
            return redirect(url_for("auction_router.list_auctions"))

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

        flash("Bid placed successfully!", "success")
        return redirect(url_for("auction_router.auction_detail", auction_id=auction.id))

    except BidTooLow:
        logger.warning(f"Bid too low: auction={auction_id}, bidder={identity}, amount={request.form.get('bid_amount')}")
        flash("Your bid must be higher than the current bid", "error")
        return redirect(url_for("auction_router.auction_detail", auction_id=auction_id))
    except Exception as e:
        logger.exception(f"Unexpected error while placing bid: auction={auction_id}, bidder={identity}")
        flash(f"Error placing bid: {str(e)}", "error")
        return redirect(url_for("auction_router.auction_detail", auction_id=auction_id))
