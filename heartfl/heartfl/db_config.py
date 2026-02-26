"""
MongoDB Database Configuration and Connection Manager
======================================================

This module initializes the MongoDB connection for the HeartFL application.

WHY THIS APPROACH:
- Centralized connection management
- Automatic reconnection handling
- Clean separation of concerns
- Easy to test and debug
- Production-ready error handling

VIVA EXPLANATION:
"We use MongoEngine to connect to MongoDB. This file initializes the connection
when Django starts, ensuring all our document models can communicate with the database.
The connection is lazy-loaded, meaning it only connects when we actually query data,
which improves startup time and resource efficiency."
"""

import mongoengine
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def connect_mongodb():
    """
    Initialize MongoDB connection using settings from Django configuration.
    
    This function is called during Django startup (in apps.py or __init__.py).
    It handles both local MongoDB and MongoDB Atlas connections.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        # Get MongoDB settings from Django config
        mongodb_settings = settings.MONGODB_SETTINGS.copy()
        db_name = settings.MONGODB_DATABASE_NAME
        
        # Check if using MongoDB Atlas (host starts with mongodb+srv://)
        host = mongodb_settings.get('host', 'localhost')
        
        if host and (host.startswith('mongodb://') or host.startswith('mongodb+srv://')):
            # MongoDB Atlas connection string - use only host
            mongoengine.connect(
                host=host,
                alias='default',
                connect=False,
                serverSelectionTimeoutMS=5000
            )
            logger.info(f"✅ MongoDB Atlas configured (lazy connection) - Database: {db_name}")
        else:
            # Local MongoDB connection - build connection properly
            connection_params = {
                'db': db_name,
                'host': mongodb_settings.get('host', 'localhost'),
                'alias': 'default',
                'connect': False
            }
            
            # Add port if specified
            if mongodb_settings.get('port'):
                connection_params['port'] = mongodb_settings['port']
            
            # Add authentication if username provided
            if mongodb_settings.get('username'):
                connection_params['username'] = mongodb_settings['username']
                connection_params['password'] = mongodb_settings.get('password', '')
                connection_params['authentication_source'] = mongodb_settings.get('authentication_source', 'admin')
            
            mongoengine.connect(**connection_params)
            logger.info(f"✅ Local MongoDB configured (lazy connection) - Database: {db_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {str(e)}")
        logger.warning("⚠️  App will continue but database operations will fail")
        logger.warning("   Please ensure MongoDB is running: mongod --dbpath /data/db")
        return False


def disconnect_mongodb():
    """
    Cleanly disconnect from MongoDB.
    Called during Django shutdown.
    """
    try:
        mongoengine.disconnect(alias='default')
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error disconnecting MongoDB: {str(e)}")


def get_database_stats():
    """
    Get MongoDB database statistics.
    Useful for debugging and monitoring.
    
    Returns:
        dict: Database statistics including collection counts
    """
    try:
        from pymongo import MongoClient
        
        # Get MongoDB settings
        mongodb_settings = settings.MONGODB_SETTINGS.copy()
        db_name = settings.MONGODB_DATABASE_NAME
        
        if 'host' in mongodb_settings and mongodb_settings['host'].startswith('mongodb+srv'):
            client = MongoClient(mongodb_settings['host'])
        else:
            client = MongoClient(
                host=mongodb_settings.get('host', 'localhost'),
                port=mongodb_settings.get('port', 27017)
            )
        
        db = client[db_name]
        
        stats = {
            'database': db_name,
            'collections': db.list_collection_names(),
            'collection_count': len(db.list_collection_names()),
        }
        
        # Get document counts for each collection
        for collection_name in stats['collections']:
            stats[f'{collection_name}_count'] = db[collection_name].count_documents({})
        
        client.close()
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get database stats: {str(e)}")
        return {'error': str(e)}
