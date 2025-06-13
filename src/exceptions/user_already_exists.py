from src.exceptions.auction_app_error import AuctionAppError

class UserAlreadyExists(AuctionAppError):
    """Raised when trying to create a user that already exists"""

    def __init__(self, message="User already exists"):
        super().__init__(message, status_code=409)
