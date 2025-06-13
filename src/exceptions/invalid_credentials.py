from src.exceptions.auction_app_error import AuctionAppError


class InvalidCredentials(AuctionAppError):
    """Raised when invalid login credentials are provided"""

    def __init__(self, message="Invalid username or password"):
        super().__init__(message, status_code=401)

