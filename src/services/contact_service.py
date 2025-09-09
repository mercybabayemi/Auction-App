from src.repositories.contact_repository import ContactMessageRepository
from src.models.contact_message import ContactMessage
import logging
logger = logging.getLogger(__name__)

class ContactMessageService:
    @staticmethod
    def create_contact_message(name, email, subject, message):
        logger.info(f"Creating contact: {name}, {email}, {subject}, {message}")
        contact_message = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )
        return ContactMessageRepository.create_contact_message(contact_message)

    @staticmethod
    def get_all_contact_messages():
        logger.debug("Fetching all contact messages")
        return ContactMessageRepository.get_all_contact_messages()

    @staticmethod
    def get_contact_message_by_id(contact_message_id):
        logger.debug("Fetching all contact messages by id")
        return ContactMessageRepository.get_contact_message_by_id(contact_message_id)

    @staticmethod
    def delete_contact_message(contact_message_id):
        logger.info(f"Deleting contact {contact_message_id}")
        return ContactMessageRepository.delete_contact_message(contact_message_id)