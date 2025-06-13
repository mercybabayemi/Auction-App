from flask_login import login_required, current_user
from mongoengine import Q

from src.exceptions.unauthorized_access import UnauthorizedAccess
from src.models.auction import Auction
from src.repositories.auction_repository import AuctionRepository
from src.repositories.user_repository import UserRepository


class AuctionService:
    @staticmethod
    def get_active_auctions():
        return AuctionRepository.get_active_auctions()

    @staticmethod
    def get_auction_by_id(auction_id):
        return AuctionRepository.get_auction_by_id(auction_id)

    @staticmethod
    @login_required
    def create_auction(item_title, item_description, starting_bid, end_time,
                     item_condition, seller, images=None, category='Other'):
        auction = AuctionRepository.create_auction(
            item_title=item_title,
            item_description=item_description,
            starting_bid=float(starting_bid),
            current_bid=float(starting_bid),
            end_time=end_time,
            item_condition=item_condition,
            seller=seller,
            status="Active",
            category=category
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
