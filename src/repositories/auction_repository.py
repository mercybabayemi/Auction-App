
"""
AuctionRepository (Persistence layer)
Responsibilities:
 - CRUD against the Auction document (mongoengine)
 - Save uploaded files (fallback) via cloudinary_service.upload_to_cloudinary
 - Delete remote images via cloudinary_service.delete_from_cloudinary
 - Return plain Python objects (Auction documents) for service layer use
"""
import logging
from datetime import datetime

from flask import current_app, url_for
from mongoengine import Q
from mongoengine.errors import DoesNotExist

from src.models.auction import Auction
from src.services.cloudinary_service import upload_to_cloudinary, delete_from_cloudinary

logger = logging.getLogger(__name__)


class AuctionRepository:
    @staticmethod
    def create_auction(item_title: str,
                       item_description: str,
                       starting_bid: float,
                       end_time,
                       item_condition: str,
                       seller,
                       images=None,
                       category: str = 'Other') -> Auction:
        """Create new auction with provided details
        images:
          - list[str] of secure_url (frontend Cloudinary uploads) -> stored directly
          - list[FileStorage] (uploaded to server) -> fallback: server-side upload to Cloudinary (upload_to_cloudinary)
        """
        auction = Auction(
            item_title=item_title,
            item_description=item_description,
            starting_bid=float(starting_bid),
            current_bid=float(starting_bid),
            end_time=end_time,
            item_condition=item_condition,
            seller=seller,
            status="Active",
            category=category
        )

        if images:
            # If the images argument is a list of strings (secure URLs) then assign directly
            if isinstance(images, list) and all(isinstance(i, str) for i in images):
                auction.image_urls = images
                logger.debug("Assigned image_urls directly from frontend-uploaded URLs.")
            else:
                # fallback: server-side file uploads
                saved_urls = AuctionRepository.save_auction_images(images)
                if saved_urls:
                    auction.image_urls = saved_urls
                    logger.debug(f"Saved {len(saved_urls)} images via server-side upload.")
                else:
                    logger.warning("No images saved from server-side upload fallback.")

        auction.save()
        logger.info(f"Created auction (id={auction.id}) title={item_title} seller={seller}")
        return auction

    @staticmethod
    def get_auction_by_id(auction_id):
        try:
            return Auction.objects.get(id=auction_id)
        except DoesNotExist:
            logger.debug(f"Auction not found with id={auction_id}")
            return None
        except Exception as exc:
            logger.error(f"Error getting auction {auction_id}: {exc}")
            return None

    @staticmethod
    def get_active_auctions():
        try:
            return Auction.objects.filter(status="Active").all()
        except Exception as e:
            logger.error(f"Error fetching active auctions: {e}")
            return []

    @staticmethod
    def get_featured_auctions(limit=6):
        try:
            return Auction.objects.filter(status="Active").order_by("-start_time").limit(limit)
        except Exception as e:
            logger.error(f"Error fetching featured auctions: {e}")
            return []

    @staticmethod
    def search_auctions(search_query=None, category=None, status=None):
        """
        Search auctions by title/description and optional category/status.
        Returns a queryset (call .all() for list).
        """
        try:
            query = Auction.objects
            if search_query:
                query = query.filter(
                    Q(item_title__icontains=search_query) | Q(item_description__icontains=search_query)
                )
            if category:
                query = query.filter(category=category)
            if status:
                query = query.filter(status=status)
            return query.all()
        except Exception as e:
            logger.error(f"Error searching auctions: {e}")
            return []

    @staticmethod
    def save_auction_images(image_files):
        """
        Upload FileStorage objects to Cloudinary via cloudinary_service.upload_to_cloudinary.
        Returns list of secure_url strings for saved images.
        """
        if not image_files:
            return []

        saved_urls = []
        for idx, image_file in enumerate(image_files):
            try:
                result = upload_to_cloudinary(image_file)
                if result and isinstance(result, dict) and result.get('secure_url'):
                    saved_urls.append(result.get('secure_url'))
                    logger.debug(f"Uploaded file #{idx} to Cloudinary: {result.get('secure_url')}")
                else:
                    # if upload_to_cloudinary returns something else, try to handle gracefully
                    logger.warning(f"Unexpected upload result for file #{idx}: {result}")
            except Exception as e:
                logger.error(f"Failed to upload file #{idx}: {e}")
                continue
        return saved_urls

    @staticmethod
    def get_image_urls(auction_id):
        auction = AuctionRepository.get_auction_by_id(auction_id)
        if auction:
            return auction.image_urls
        return []

    @staticmethod
    def get_primary_image_url(auction_id):
        auction = AuctionRepository.get_auction_by_id(auction_id)
        if auction and auction.image_urls:
            return auction.image_urls[0]
        # fallback to static placeholder
        try:
            return url_for('static', filename='uploads/auction_images/default-auction.jpg')
        except Exception:
            # if url_for is not available (e.g., called outside app context), return None
            logger.debug("url_for not available for default image; returning None")
            return None

    @staticmethod
    def update_auction(auction_id, **updated_fields):
        """
        Update allowed fields on Auction. We fetch the document, update fields and save.
        Returns updated Auction or None if not found.
        """
        auction = AuctionRepository.get_auction_by_id(auction_id)
        if not auction:
            logger.debug(f"Cannot update - auction not found: {auction_id}")
            return None

        # allowed updates — keep it conservative
        allowed = {
            'item_title', 'item_description', 'starting_bid', 'current_bid',
            'item_condition', 'end_time', 'category', 'status', 'image_urls'
        }

        for key, value in updated_fields.items():
            if key in allowed:
                setattr(auction, key, value)
                logger.debug(f"Set {key} for auction {auction_id}")
            else:
                logger.debug(f"Skipped update field {key} (not allowed)")

        auction.save()
        logger.info(f"Auction updated (id={auction_id})")
        return auction

    @staticmethod
    def delete_auction_images(image_urls):
        """
        Delete images from Cloudinary. Accepts a list of secure_urls or public_ids and attempts to delete each.
        """
        if not image_urls:
            logger.debug("No image URLs provided for deletion.")
            return

        for url in image_urls:
            try:
                result = delete_from_cloudinary(url)
                if result:
                    logger.info(f"Deleted Cloudinary asset for {url}")
                else:
                    logger.warning(f"Cloudinary delete returned False for {url}")
            except Exception as e:
                logger.error(f"Error deleting Cloudinary asset {url}: {e}")

    @staticmethod
    def delete_auction(auction_id):
        """
        Delete auction and its images (if any). Returns True if deleted else False.
        """
        auction = AuctionRepository.get_auction_by_id(auction_id)
        if not auction:
            logger.debug(f"Delete requested for non-existent auction {auction_id}")
            return False

        # delete remote images (best-effort)
        if auction.image_urls:
            AuctionRepository.delete_auction_images(auction.image_urls)

        auction.delete()
        logger.info(f"Auction deleted (id={auction_id})")
        return True

    @staticmethod
    def close_auction(auction_id):
        """
        Mark auction as completed.
        """
        auction = AuctionRepository.get_auction_by_id(auction_id)
        if not auction:
            logger.debug(f"Close requested for non-existent auction {auction_id}")
            return None
        if auction.status == 'Active':
            auction.status = 'Completed'
            auction.save()
            logger.info(f"Auction closed (id={auction_id})")
        return auction