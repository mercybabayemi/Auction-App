from src.exceptions.auction_app_error import AuctionAppError


class InvalidBid(AuctionAppError):
    """Raised when an invalid bid is placed"""

    def __init__(self, message="Invalid bid amount"):
        super().__init__(message, status_code=400)

