"""
AuctionService (Business / Domain layer)
 - Enforces business rules and validation
 - Orchestrates repository calls
 - Keeps controller (router) thin
"""
import logging
from datetime import datetime

from flask import current_app

from src.repositories.auction_repository import AuctionRepository

logger = logging.getLogger(__name__)


class AuctionService:
    @staticmethod
    def _parse_end_time(end_time_input):
        """
        Accept either a datetime or an ISO string and return a datetime.
        Raises ValueError if parsing fails.
        """
        if end_time_input is None:
            raise ValueError("end_time is required")
        if isinstance(end_time_input, datetime):
            return end_time_input
        # try parsing ISO-formatted string
        try:
            return datetime.fromisoformat(end_time_input)
        except Exception as e:
            logger.debug(f"Failed to parse end_time '{end_time_input}': {e}")
            raise ValueError("end_time must be a valid ISO datetime string")

    @staticmethod
    def create_auction(payload: dict, seller_id):
        """
        payload expected to include:
          - item_title (str)
          - item_description (str)
          - starting_bid (float or numeric string)
          - end_time (ISO datetime string or datetime)
          - item_condition (str)
          - category (optional)
          - image_urls (list[str]) or images (list FileStorage)
        """
        logger.debug("AuctionService.create_auction called")

        # Required fields
        for field in ['item_title', 'item_description', 'starting_bid', 'end_time', 'item_condition']:
            if not payload.get(field):
                logger.warning(f"Missing required field: {field}")
                raise ValueError(f"{field} is required")

        # Validate starting bid
        try:
            starting_bid_val = float(payload.get('starting_bid'))
            if starting_bid_val <= 0:
                raise ValueError("starting_bid must be greater than 0")
        except ValueError:
            logger.warning("Invalid starting_bid value")
            raise ValueError("starting_bid must be a number greater than 0")

        # Parse and validate end_time
        end_time = AuctionService._parse_end_time(payload.get('end_time'))
        if end_time <= datetime.utcnow():
            logger.warning(f"end_time is not in the future: {end_time.isoformat()}")
            raise ValueError("end_time must be in the future")

        # images: prefer image_urls (strings) if provided by frontend uploads
        image_urls = payload.get('image_urls')
        images_files = payload.get('images')  # optional server-file fallback

        if not image_urls and not images_files:
            logger.warning("No images provided for new auction")
            raise ValueError("At least one image is required")

        images_payload = image_urls if image_urls else images_files
        logger.debug(f"Images payload being sent to AuctionRepository: {images_payload}")
        # Build domain data and delegate to repository
        auction = AuctionRepository.create_auction(
            item_title=payload['item_title'],
            item_description=payload['item_description'],
            starting_bid=starting_bid_val,
            end_time=end_time,
            item_condition=payload['item_condition'],
            seller=seller_id,
            images=images_payload,
            category=payload.get('category', 'Other')
        )

        logger.info(f"AuctionService created auction id={auction.id} by seller={seller_id}")
        return auction

    @staticmethod
    def get_auction_by_id(auction_id):
        logger.debug(f"AuctionService.get_auction_by_id: {auction_id}")
        auction = AuctionRepository.get_auction_by_id(auction_id)
        if not auction:
            logger.info(f"Auction not found: {auction_id}")
        return auction

    @staticmethod
    def search_auctions(search_query=None, category=None, status=None):
        logger.debug("AuctionService.search_auctions called")
        return AuctionRepository.search_auctions(search_query=search_query, category=category, status=status)

    @staticmethod
    def get_featured_auctions(limit=6):
        auctions = AuctionRepository.get_featured_auctions(limit)
        return auctions

    @staticmethod
    def update_auction(auction_id, updated_data, current_user_id=None):
        """
        Business checks for update:
         - If you want to restrict updates to the seller, pass current_user_id and check ownership.
         - Example: only seller can change item_title, description, images etc.
        """
        auction = AuctionRepository.get_auction_by_id(auction_id)
        if not auction:
            logger.warning(f"Update attempted on non-existent auction {auction_id}")
            return None

        # Optional authorization: only seller may update
        if current_user_id and str(auction.seller.id) != str(current_user_id):
            logger.warning(f"Unauthorized update attempt by {current_user_id} on auction {auction_id}")
            raise PermissionError("You are not authorized to update this auction")

        # Basic rule: cannot update a completed auction
        if auction.status == 'Completed':
            logger.warning(f"Attempted update on completed auction {auction_id}")
            raise ValueError("Cannot update a completed auction")

        # Validate any fields that need domain checks
        if 'starting_bid' in updated_data:
            try:
                sb = float(updated_data['starting_bid'])
                if sb <= 0:
                    raise ValueError("starting_bid must be greater than 0")
            except ValueError:
                raise ValueError("starting_bid must be a valid number")

        if 'end_time' in updated_data:
            end_time = AuctionService._parse_end_time(updated_data['end_time'])
            if end_time <= datetime.utcnow():
                raise ValueError("end_time must be in the future")
            updated_data['end_time'] = end_time

        # Delegate update to repository
        updated = AuctionRepository.update_auction(auction_id, **updated_data)
        logger.info(f"Auction {auction_id} updated by {current_user_id}")
        return updated

    @staticmethod
    def delete_auction(auction_id, current_user_id=None):
        """
        Business rule: Only seller (or admin) can delete an auction.
        If current_user_id is provided, check ownership.
        """
        auction = AuctionRepository.get_auction_by_id(auction_id)
        if not auction:
            logger.warning(f"Delete attempted on non-existent auction {auction_id}")
            return False

        if current_user_id and str(auction.seller.id) != str(current_user_id):
            logger.warning(f"Unauthorized delete attempt by {current_user_id} on {auction_id}")
            raise PermissionError("You are not authorized to delete this auction")

        result = AuctionRepository.delete_auction(auction_id)
        logger.info(f"Auction {auction_id} deleted by {current_user_id}")
        return result

    @staticmethod
    def close_auction(auction_id):
        return AuctionRepository.close_auction(auction_id)
