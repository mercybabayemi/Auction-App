from src.exceptions.auction_app_error import AuctionAppError


class AuctionNotFound(AuctionAppError):
    """Raised when an auction is not found"""

    def __init__(self, message="Auction not found"):
        super().__init__(message, status_code=404)

