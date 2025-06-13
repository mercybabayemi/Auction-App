class AuctionAppError(Exception):
    """Base exception class for the Auction App"""

    def __init__(self, message="An error occurred in the Auction App", status_code=400, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self):
        rv = dict(self.payload)
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv

