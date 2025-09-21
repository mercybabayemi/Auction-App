from mongoengine import Document, FloatField, ReferenceField, DateTimeField
from datetime import datetime

class Bid(Document):
    auction_id = ReferenceField('Auction', required=True)
    bidder_id = ReferenceField('User', required=True)
    bid_amount = FloatField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)  # add timestamp

    meta = {'collection': 'bid'}
