from src.exceptions.auction_app_error import AuctionAppError


class BidTooLow(AuctionAppError):
    """Raised when a bid is lower than the current bid"""

    def __init__(self, message="Bid amount must be higher than current bid"):
        super().__init__(message, status_code=400)
