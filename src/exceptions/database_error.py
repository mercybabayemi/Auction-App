from src.exceptions.auction_app_error import AuctionAppError


class DatabaseError(AuctionAppError):
    """Raised when there's a database operation error"""

    def __init__(self, message="Database operation failed"):
        super().__init__(message, status_code=500)
