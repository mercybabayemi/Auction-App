from src.exceptions.auction_app_error import AuctionAppError


class UnauthorizedAccess(AuctionAppError):
    """Raised when user tries to access unauthorized resource"""

    def __init__(self, message="Unauthorized access"):
        super().__init__(message, status_code=403)
