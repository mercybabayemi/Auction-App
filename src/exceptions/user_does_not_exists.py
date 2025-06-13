from src.exceptions.auction_app_error import AuctionAppError

class UserDoesNotExist(AuctionAppError):
    """Raised when trying to create a user that already exists"""

    def __init__(self, message="User does not exists"):
        super().__init__(message, status_code=409)
