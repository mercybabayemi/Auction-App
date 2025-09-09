import logging
from src.exceptions.bid_too_low import BidTooLow
from src.exceptions.invalid_bid import InvalidBid
from src.models.auction import Auction
from src.repositories.auction_repository import AuctionRepository
from src.repositories.bid_repository import BidRepository

logger = logging.getLogger(__name__)

class BidService:
    @staticmethod
    def get_bids_for_auction(auction_id):
        logger.info(f"Fetching bids for auction {auction_id}")
        return BidRepository.get_bids_for_auction(auction_id)

    @staticmethod
    def place_bid(auction_id, bidder_id, bid_amount):
        logger.info(f"Attempting to place bid: auction={auction_id}, bidder={bidder_id}, amount={bid_amount}")

        highest_bid = BidRepository.get_highest_bid(auction_id)
        highest_bid_amount = highest_bid.bid_amount
        logger.debug(f"Highest bid returned from repo: {highest_bid}")

        if highest_bid is None:
            auction = AuctionRepository.get_auction_by_id(auction_id)
            highest_bid_amount = auction.starting_bid
            logger.debug(f"No bids found, using auction starting_bid={highest_bid}")

        if bid_amount <= highest_bid_amount:
            logger.warning(f"Bid too low: amount={bid_amount}, required > {highest_bid}")
            raise BidTooLow()

        logger.info(f"Bid accepted, saving to repo: auction={auction_id}, bidder={bidder_id}, amount={bid_amount}")
        return BidRepository.place_bid(auction_id, bidder_id, bid_amount)

    @staticmethod
    def get_highest_bid(auction_id):
        highest = BidRepository.get_highest_bid(auction_id)
        logger.debug(f"Highest bid for auction {auction_id}: {highest}")
        return highest

    @staticmethod
    def get_user_bids(bidder_id):
        logger.debug(f"Fetching user bids for bidder {bidder_id}")
        return BidRepository.get_user_bids(bidder_id)
