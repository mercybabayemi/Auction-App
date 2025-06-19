from mongoengine import Q
from src.models.auction import Auction
from src.repositories.auction_repository import AuctionRepository


class AuctionService:
    @staticmethod
    def get_active_auctions():
        return AuctionRepository.get_active_auctions()

    @staticmethod
    def get_auction_by_id(auction_id):
        return AuctionRepository.get_auction_by_id(auction_id)

    @staticmethod
    def create_auction(item_title, item_description, starting_bid, end_time,
                     item_condition, seller, images=None, category='Other'):
        auction = Auction(
            item_title=item_title,
            item_description=item_description,
            starting_bid=float(starting_bid),
            current_bid=float(starting_bid),
            end_time=end_time,
            item_condition=item_condition,
            seller=seller,
            status="Active",  # Should be pending until approved
            category=category,
            images=images,
        )
        return auction


    @staticmethod
    def get_featured_auctions():
        return AuctionRepository.get_featured_auctions()

    @staticmethod
    def search_auctions(search_query=None, category=None, status=None):
        query = Auction.objects()

        if search_query:
            query = query.filter(
                Q(item_title__icontains=search_query) | Q(item_description__icontains=search_query)
            )

        if category:
            query = query.filter(category=category)

        return query.all()
