"""Data Access Layer for MongoDB Cache Management (PyMongo 4.10.1)"""

import logging
from datetime import datetime
import hashlib
import re

from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

try:
    from django.conf import settings
    DJANGO_AVAILABLE = settings.configured
except ImportError:
    DJANGO_AVAILABLE = False

logger = logging.getLogger(__name__)

# --- CacheManager Class (PyMongo 4.x implementation) ---
class CacheManager:
    """Native PyMongo-based cache manager."""
    
    def __init__(self, connection_string: str = None, database_name: str = None, 
                 collection_name: str = None, ttl_seconds: int = None, **connection_options):
        
        if DJANGO_AVAILABLE and hasattr(settings, 'MONGODB_SETTINGS'):
            # Load config from settings.py (data_explorer.settings)
            mongodb_settings = settings.MONGODB_SETTINGS
            pool_settings = mongodb_settings.get('CONNECTION_POOL', {})
            
            self.connection_string = mongodb_settings.get('CONNECTION_STRING')
            self.database_name = mongodb_settings.get('DATABASE_NAME')
            self.collection_name = mongodb_settings.get('CACHE_COLLECTION')
            self.ttl_seconds = mongodb_settings.get('CACHE_TTL_SECONDS')
            
            connection_options.update({
                'serverSelectionTimeoutMS': pool_settings.get('serverSelectionTimeoutMS'),
                'maxPoolSize': pool_settings.get('maxPoolSize'),
                # ... (other PyMongo 4.x options)
            })
        
        # ... (rest of configuration and client setup logic) ...
        
        try:
            self.client = MongoClient(self.connection_string, **connection_options)
            self.client.admin.command('ping') 
            
            self.db = self.client[self.database_name]
            self.collection: Collection = self.db[self.collection_name]
            self._setup_ttl_index()
            
            logger.info(f"Cache manager initialized for {self.database_name}.{self.collection_name}. TTL: {self.ttl_seconds}s")
                    
        except ServerSelectionTimeoutError:
            logger.error("Failed to connect to MongoDB - server selection timeout")
            raise
        except PyMongoError as e:
            logger.error(f"Failed to initialize MongoDB connection: {e}")
            raise
            
    def _setup_ttl_index(self):
        # ... (TTL index creation logic using self.collection.create_index) ...
        pass # Placeholder for full implementation

    def get_result(self, key):
        # ... (implementation) ...
        pass
    
    def set_result(self, key, data):
        # ... (implementation) ...
        pass

    def get_cache_stats(self):
        # ... (implementation) ...
        return {'total_entries': 0, 'ttl_seconds': self.ttl_seconds}

    def health_check(self):
        """Test MongoDB connectivity."""
        self.client.admin.command('ping')

_cache_manager = None
def get_cache_manager():
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

def generate_cache_key(sparql_query: str) -> str:
    # ... (key generation logic) ...
    return f"sparql_{hashlib.sha256(sparql_query.encode()).hexdigest()[:16]}"