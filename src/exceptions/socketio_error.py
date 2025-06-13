from src.exceptions.auction_app_error import AuctionAppError


class SocketIOError(AuctionAppError):
    """Raised for SocketIO specific errors"""

    def __init__(self, message="SocketIO operation failed"):
        super().__init__(message, status_code=400)