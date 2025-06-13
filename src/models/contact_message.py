from mongoengine import Document, StringField, DateTimeField
from datetime import datetime

class ContactMessage(Document):
    name = StringField(max_length=100, required=True)
    email = StringField(max_length=100, required=True)
    subject = StringField(max_length=200, required=True)
    message = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'contact_messages'
    }

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'subject': self.subject,
            'message': self.message,
            'created_at': self.created_at
        }

