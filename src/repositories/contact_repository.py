from src.models.contact_message import ContactMessage

class ContactMessageRepository:
    @staticmethod
    def create_contact_message(contact_message):
        contact_message.save()
        return contact_message

    @staticmethod
    def get_all_contact_messages():
        return ContactMessage.objects().all()

    @staticmethod
    def get_contact_message_by_id(contact_message_id):
        return ContactMessage.objects(id=contact_message_id).first()

    @staticmethod
    def delete_contact_message(contact_message_id):
        contact_message = ContactMessage.objects(id=contact_message_id).first()
        if contact_message:
            contact_message.delete()
            return True
        return False