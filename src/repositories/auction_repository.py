import os
from datetime import datetime

from flask import current_app
from flask_login import current_user
from werkzeug.utils import secure_filename

from src.models.auction import Auction

class AuctionRepository:
    @staticmethod
    def get_active_auctions():
        """Get all approved and active auctions"""
        return Auction.objects.filter(is_approved=True, status="Active")

    @staticmethod
    def get_auction_by_id(auction_id):
        """Get single auction by ID"""
        return Auction.objects.get(id=auction_id)

    @staticmethod
    def save_auction_image(image_file):
        """Save uploaded image and return filename"""
        if not image_file:
            return None

        filename = secure_filename(f"{datetime.now().timestamp()}_{image_file.filename}")
        save_path = os.path.join(current_app.config['AUCTION_IMAGES_FOLDER'], filename)
        image_file.save(save_path)
        return filename

    @staticmethod
    def create_auction(item_title, item_description, starting_bid, end_time,
                      item_condition, seller, images=None, category='Other'):
        """Create new auction with provided details"""
        auction = Auction(
            item_title=item_title,
            item_description=item_description,
            starting_bid=float(starting_bid),
            current_bid=float(starting_bid),
            end_time=end_time,
            item_condition=item_condition,
            seller=seller,
            status="Pending",  # Should be pending until approved
            category=category,
            is_approved=False  # Default to not approved
        )

        if images:
            auction.image_filenames = [AuctionRepository.save_auction_image(img) for img in images]

        auction.save()
        return auction

    @staticmethod
    def get_featured_auctions(limit=6):
        """Get featured active auctions"""
        return Auction.objects.filter(is_approved=True, status="Active").order_by("-start_time").limit(limit)

    @staticmethod
    def approve(auction_id):
        """
        Approve the auction for public listing
        Args:
            auction_id: ID of the auction to approve
        Returns:
            The approved auction
        """
        auction = Auction.objects.get(id=auction_id)
        if not auction.is_approved:
            auction.is_approved = True
            if auction.status == "Pending":
                auction.status = "Active"
            auction.save()
        return auction

    @staticmethod
    def close_auction(auction_id):
        """
        Mark auction as completed
        Args:
            auction_id: ID of the auction to close
        Returns:
            The closed auction
        """
        auction = Auction.objects.get(id=auction_id)
        if auction.status == 'Active':
            auction.status = 'Completed'
            auction.save()
        return auction