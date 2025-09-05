# src/services/cloudinary_service.py
"""
Cloudinary helper utilities (server-side).
 - upload_to_cloudinary(file): server-side fallback upload (returns response dict with secure_url)
 - delete_from_cloudinary(public_id_or_url): accepts public_id or secure_url and destroys asset
 - extract_public_id_from_url(url): helper to turn secure_url -> Cloudinary public_id
NOTE: Primary upload flow in this project is frontend -> Cloudinary (unsigned preset).
      This module is retained for deletion and a server-upload fallback.
"""
import logging
import os
from datetime import datetime

import cloudinary
import cloudinary.uploader

from flask import current_app
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)


def configure_cloudinary():
    cloudinary.config(
        cloud_name=current_app.config.get('CLOUDINARY_CLOUD_NAME'),
        api_key=current_app.config.get('CLOUDINARY_API_KEY'),
        api_secret=current_app.config.get('CLOUDINARY_API_SECRET'),
        secure=True
    )


def extract_public_id_from_url(url: str):
    """
    Example secure_url:
    https://res.cloudinary.com/<cloud_name>/image/upload/v169.../auction_app/images/filename.jpg
    We return: auction_app/images/filename  (without extension)
    """
    if not url or not isinstance(url, str):
        return None
    try:
        parts = url.split('/upload/')
        if len(parts) < 2:
            return None
        tail = parts[1]
        # strip version if present (v123456/)
        if tail.startswith('v') and '/' in tail:
            tail = tail.split('/', 1)[1]
        # strip querystring
        tail = tail.split('?', 1)[0]
        # remove extension
        public_with_ext = tail
        public_id = public_with_ext.rsplit('.', 1)[0]
        return public_id
    except Exception as e:
        logger.error(f"extract_public_id_from_url error for {url}: {e}")
        return None


def upload_to_cloudinary(file, folder=None):
    """
    Server-side upload using cloudinary.uploader.upload
    Returns Cloudinary response dict (includes 'secure_url' and 'public_id') or raises Exception.
    """
    configure_cloudinary()

    if not file or not getattr(file, 'filename', None):
        logger.debug("upload_to_cloudinary: no file provided")
        return None

    # Validate extension
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'jpg', 'jpeg', 'png', 'gif', 'webp'})
    filename = secure_filename(file.filename)
    if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in allowed:
        raise ValueError("Invalid file type")

    # Validate size if possible
    max_size = current_app.config.get('MAX_IMAGE_SIZE', 5 * 1024 * 1024)
    try:
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > max_size:
            raise ValueError("File too large")
    except Exception:
        # Some file-like objects may not support tell/seek; rely on cloudinary to validate
        logger.debug("Could not determine file size before upload (streaming upload).")

    # Create unique filename to avoid collisions if desired
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{timestamp}"

    upload_folder = folder or current_app.config.get('CLOUDINARY_UPLOAD_FOLDER', 'auction_app/images')

    try:
        response = cloudinary.uploader.upload(
            file,
            folder=upload_folder,
            public_id=unique_filename,
            overwrite=False,
            resource_type='image',
            quality='auto',
            fetch_format='auto'
        )
        logger.info(f"Uploaded file to Cloudinary: {response.get('secure_url')}")
        return response
    except Exception as e:
        logger.exception(f"Cloudinary upload error: {e}")
        raise


def delete_from_cloudinary(public_id_or_url: str) -> bool:
    """
    Deletes an asset in Cloudinary. Accepts:
      - public_id (e.g., 'auction_app/images/filename')
      - secure_url (extracts public_id)
    Returns True on success.
    """
    configure_cloudinary()

    if not public_id_or_url:
        logger.debug("delete_from_cloudinary called with empty value")
        return False

    # If it's a URL, try to extract public_id
    public_id = public_id_or_url
    if public_id_or_url.startswith('http'):
        public_id = extract_public_id_from_url(public_id_or_url)
        if not public_id:
            logger.warning(f"Could not extract public_id from URL: {public_id_or_url}")
            return False

    try:
        resp = cloudinary.uploader.destroy(public_id)
        result = resp.get('result')
        logger.info(f"Cloudinary destroy for {public_id}: {resp}")
        return result == 'ok'
    except Exception as e:
        logger.exception(f"Cloudinary destroy error for {public_id}: {e}")
        return False