from src.exceptions.bid_too_low import BidTooLow
from src.exceptions.invalid_bid import InvalidBid
from src.repositories.bid_repository import BidRepository

class BidService:
    @staticmethod
    def get_bids_for_auction(auction_id):
        return BidRepository.get_bids_for_auction(auction_id)

    @staticmethod
    def place_bid(auction_id, bidder_id, bid_amount):
        bid_id = BidRepository.get_bid_id_by_bidder(bidder_id)
        if bid_amount < BidRepository.get_bid_amount(bid_id):
            return BidRepository.place_bid(auction_id, bidder_id, bid_amount)
        else:
            raise BidTooLow

    @staticmethod
    def get_highest_bid(auction_id):
        if BidRepository.get_highest_bid(auction_id):
            return BidRepository.get_highest_bid(auction_id)
        else:
            raise InvalidBid