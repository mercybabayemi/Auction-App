from src.exceptions.auction_app_error import AuctionAppError


class AuctionEnded(AuctionAppError):
    """Raised when trying to bid on an ended auction"""

    def __init__(self, message="Auction has already ended"):
        super().__init__(message, status_code=400)
