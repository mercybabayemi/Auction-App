from src.models.bid import Bid

class BidRepository:
    @staticmethod
    def get_bid_amount(auction_id):
        return Bid.objects.get(id=auction_id).bid_amount

    @staticmethod
    def get_bids_for_auction(auction_id):
        return Bid.objects(auction_id=auction_id).order_by('-bid_amount')

    @staticmethod
    def place_bid(auction_id, bidder_id, bid_amount):
        bid = Bid(
            auction_id=auction_id,
            bidder_id=bidder_id,
            bid_amount=bid_amount
        )
        bid.save()
        return bid

    @staticmethod
    def get_bid_id_by_bidder(bidder_id):
        return Bid.objects.get(bidder_id=bidder_id).id


    @staticmethod
    def get_highest_bid(auction_id):
        #return Bid.objects.get(auction_id=auction_id).order_by('bid_amount').first().bid_amount
        return Bid.objects(auction_id=auction_id).order_by('-bid_amount').first()
