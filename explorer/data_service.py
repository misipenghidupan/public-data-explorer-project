import logging
from datetime import datetime, timedelta
from pymongo import MongoClient, errors
from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE, XML, CSV
from django.conf import settings

logger = logging.getLogger(__name__)

class DataService:
    """
    Handles data interaction, including SPARQL queries and MongoDB caching.
    Implements a 24-hour TTL caching mechanism.
    """
    _mongo_client = None
    _collection = None
    
    # 24-hour TTL in seconds
    CACHE_TTL_SECONDS = 24 * 60 * 60 

    def __init__(self):
        """Initializes MongoDB connection and sets up cache collection."""
        if DataService._mongo_client is None:
            try:
                # Initialize client and connect
                DataService._mongo_client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
                # The ismaster command is a cheap way to verify a connection
                DataService._mongo_client.admin.command('ismaster')
                db = DataService._mongo_client[settings.MONGO_DATABASE]
                DataService._collection = db[settings.MONGO_COLLECTION_CACHE]
                logger.info("MongoDB connection established.")
                
                # Ensure the cache collection has a TTL index
                self._ensure_ttl_index()

            except errors.ConnectionError as e:
                logger.error(f"MongoDB connection failed: {e}")
                DataService._mongo_client = None
                DataService._collection = None

    def _ensure_ttl_index(self):
        """Creates a TTL index on the 'timestamp' field."""
        if DataService._collection is not None:
            # Check if index exists
            index_info = DataService._collection.index_information()
            
            # Find the index with the correct key and options
            ttl_index_name = None
            for name, info in index_info.items():
                if info.get('key') == [('timestamp', 1)] and info.get('expireAfterSeconds') == self.CACHE_TTL_SECONDS:
                    ttl_index_name = name
                    break

            if ttl_index_name is None:
                # Create a new TTL index
                # Drop existing index if it has the wrong TTL value
                try:
                    DataService._collection.drop_index("timestamp_1")
                except errors.OperationFailure:
                    pass # Index did not exist or was named differently
                    
                DataService._collection.create_index(
                    "timestamp", 
                    expireAfterSeconds=self.CACHE_TTL_SECONDS,
                    name="timestamp_ttl_index" # Custom name for clarity
                )
                logger.info(f"MongoDB TTL index created/ensured on '{settings.MONGO_COLLECTION_CACHE}'.")

    @property
    def is_db_connected(self):
        """Returns True if the MongoDB collection is available."""
        return self._collection is not None

    def get_cached_result(self, key):
        """
        Retrieves a result from cache. The TTL is handled by the MongoDB index.
        Returns the cached data or None if not found or expired.
        """
        if not self.is_db_connected:
            return None
        
        try:
            document = self._collection.find_one({'_id': key})
            if document:
                # Explicit check is now technically redundant due to TTL index, 
                # but good for safety and immediate user feedback if index fails.
                # However, relying on the index is the primary mechanism.
                logger.info(f"Cache hit for key: {key}")
                return document['data']
        except Exception as e:
            logger.error(f"Error fetching from cache: {e}")
            
        return None

    def set_cached_result(self, key, data):
        """Stores a result in cache with the current timestamp."""
        if not self.is_db_connected:
            return
            
        try:
            self._collection.update_one(
                {'_id': key},
                {'$set': {'data': data, 'timestamp': datetime.utcnow()}},
                upsert=True
            )
            logger.info(f"Cache miss/update, stored result for key: {key}")
        except Exception as e:
            logger.error(f"Error storing to cache: {e}")

    def execute_sparql_query(self, query):
        """
        Executes a SPARQL query against the Wikidata endpoint.
        Returns a tuple (head_vars, results_list) or raises an exception.
        """
        # 1. Check Cache
        cached_data = self.get_cached_result(query)
        if cached_data:
            return cached_data['head_vars'], cached_data['results']

        # 2. Execute Query
        try:
            sparql = SPARQLWrapper(settings.WIKIDATA_ENDPOINT)
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            
            head_vars = results['head']['vars']
            results_list = []
            
            for binding in results['results']['bindings']:
                row = {}
                for var in head_vars:
                    # Extract the value from the binding dictionary structure
                    row[var] = binding.get(var, {}).get('value', '')
                results_list.append(row)

            # 3. Store Cache
            new_data = {'head_vars': head_vars, 'results': results_list}
            self.set_cached_result(query, new_data)
            
            return head_vars, results_list
            
        except Exception as e:
            logger.error(f"SPARQL execution failed: {e}")
            raise RuntimeError(f"SPARQL execution failed: {e}")