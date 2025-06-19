from datetime import datetime

from mongoengine import Document, StringField, DateTimeField, FloatField, ListField, ReferenceField, BooleanField


class Auction(Document):
    item_title = StringField(required=True)
    item_description = StringField(required=True)
    starting_bid = FloatField(required=True, min_value=0.01)
    current_bid = FloatField(default=0.0)
    item_condition = StringField(required=True, choices=['New', 'Like New', 'Used', 'Refurbished'])
    seller = ReferenceField('User', required=True)
    status = StringField(default='Active', choices=['Active', 'Completed', 'Cancelled'])
    bids = ListField(ReferenceField('Bid'), default=list)
    image_filenames = ListField(StringField(), default=list)
    start_time = DateTimeField(default=datetime.utcnow)
    end_time = DateTimeField(required=True)
    category = StringField(choices=['Electronics', 'Fashion', 'Home', 'Collectibles', 'Other'])

    def to_dict(self):
        return {
            'id': str(self.id),
            'item_title': self.item_title,
            'item_description': self.item_description,
            'starting_bid': self.starting_bid,
            'current_bid': self.current_bid,
            'item_condition': self.item_condition,
            'seller': str(self.seller.id),
            'status': self.status,
            'image_filenames': self.image_filenames,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'category': self.category,
            'bid_count': len(self.bids)
        }

    meta = {'collection': 'auction'}