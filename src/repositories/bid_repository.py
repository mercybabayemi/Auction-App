import logging
logger = logging.getLogger(__name__)

from src.models.bid import Bid

class BidRepository:
    @staticmethod
    def get_bid_amount(auction_id):
        logger.debug(f"Fetching bid amount for auction id{auction_id}")
        return Bid.objects.get(auction_id=auction_id).bid_amount

    @staticmethod
    def get_bids_for_auction(auction_id):
        logger.debug(f"Fetching bids for auction {auction_id}")
        return Bid.objects(auction_id=auction_id).order_by('-bid_amount')

    @staticmethod
    def place_bid(auction_id, bidder_id, bid_amount):
        logger.info(f"Placing bid: auction={auction_id}, bidder={bidder_id}, amount={bid_amount}")
        bid = Bid(
            auction_id=auction_id,
            bidder_id=bidder_id,
            bid_amount=bid_amount
        )
        bid.save()
        logger.info(f"Bid saved: id={bid.id}")
        return bid

    @staticmethod
    def get_bid_id_by_bidder(bidder_id):
        logger.debug(f"Fetching bid by bidder id {bidder_id}")
        return Bid.objects.get(bidder_id=bidder_id).id


    @staticmethod
    def get_highest_bid(auction_id):
        logger.debug(f"Fetching highest bid for auction {auction_id}")
        return Bid.objects(auction_id=auction_id).order_by('-bid_amount').first()


    @staticmethod
    def get_user_bids(bidder_id):
        logger.debug(f"Fetching user bids for bidder {bidder_id}")
        return Bid.objects(bidder_id=bidder_id).select_related()