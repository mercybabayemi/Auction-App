from src.models.contact_message import ContactMessage
import logging
logger = logging.getLogger(__name__)


class ContactMessageRepository:
    @staticmethod
    def create_contact_message(contact_message):
        logger.info(f"Creating contact entry: {contact_message}")
        contact_message.save()
        logger.debug(f"Contact created: {contact_message.id}")
        return contact_message

    @staticmethod
    def get_all_contact_messages():
        logger.debug("Fetching all contact messages")
        return ContactMessage.objects().all()

    @staticmethod
    def get_contact_message_by_id(contact_message_id):
        logger.debug("Fetching all contact messages")
        return ContactMessage.objects(id=contact_message_id).first()

    @staticmethod
    def delete_contact_message(contact_message_id):
        logger.info(f"Deleting contact {contact_message_id}")
        contact_message = ContactMessage.objects(id=contact_message_id).first()
        if contact_message:
            contact_message.delete()
            return True
        return False