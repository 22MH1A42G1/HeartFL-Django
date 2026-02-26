"""
Django AppConfig for HeartFL Project
Initializes MongoDB connection when Django starts
"""

from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class HeartflConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'heartfl'
    
    def ready(self):
        """
        Called when Django starts.
        Initialize MongoDB connection here.
        """
        try:
            from .db_config import connect_mongodb
            connect_mongodb()
            logger.info("HeartFL app initialized with MongoDB")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB: {str(e)}")
