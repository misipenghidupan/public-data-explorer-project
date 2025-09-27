import logging
from django.conf import settings
from pymongo import MongoClient, ASCENDING, IndexModel

logger = logging.getLogger('explorer')

class MongoCacheManager:
    """
    Handles connection and operations for the MongoDB cache.
    Configuration is read directly from Django settings (settings.MONGODB_SETTINGS).
    """
    def __init__(self):
        """Initializes the MongoDB connection and ensures the TTL index exists."""
        try:
            # 1. Get settings
            mongo_settings = settings.MONGODB_SETTINGS

            self.client = MongoClient(mongo_settings['URI'])
            self.db = self.client[mongo_settings['DATABASE']]
            self.collection = self.db[mongo_settings['CACHE_COLLECTION']]
            self.ttl_seconds = mongo_settings['TTL_SECONDS']

            logger.info("Successfully connected to MongoDB database '%s'.", mongo_settings['DATABASE'])
            
            # 2. Ensure TTL Index for automatic expiration
            self._ensure_ttl_index()

        except Exception as e:
            logger.error("Failed to initialize MongoDB connection or cache manager: %s", e)
            # Raise the exception to prevent the app from continuing without cache
            raise

    def _ensure_ttl_index(self):
        """Creates a TTL index on the 'created_at' field if it doesn't already exist."""
        
        # Define the index model
        # FIX: Changed 'ttl_index' to 'explorer_ttl_index' to match the existing index name reported by MongoDB.
        INDEX_NAME = "explorer_ttl_index"
        ttl_index = IndexModel([("created_at", ASCENDING)], 
                                expireAfterSeconds=self.ttl_seconds, 
                                name=INDEX_NAME)
        
        # Check existing indexes to avoid creation conflict
        index_names = self.collection.index_information().keys()
        
        if INDEX_NAME not in index_names:
            self.collection.create_indexes([ttl_index])
            logger.info("TTL index for cache collection created.")
        else:
            # Now we use the correct name when verifying the index exists
            logger.info("TTL index for cache collection verified.")


    def get(self, key):
        """Retrieves a cached item by key."""
        document = self.collection.find_one({"_id": key})
        if document:
            # The cached document stores the result in a 'data' field
            return document.get('data')
        return None

    def set(self, key, value):
        """Stores an item in the cache."""
        import datetime
        
        document = {
            "_id": key,
            "data": value,
            "created_at": datetime.datetime.now(datetime.UTC)
        }
        
        # Use replace_one with upsert=True to create or update the document
        self.collection.replace_one(
            {"_id": key}, 
            document, 
            upsert=True
        )
