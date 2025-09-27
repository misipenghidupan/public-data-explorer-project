"""
Data Service Layer: Handles all interactions with the Wikidata SPARQL endpoint.
Implements caching, timeout, and custom exceptions.
"""
import logging
import time
import json
from django.conf import settings

# Import our new DAL
from .dal.cache_manager import get_cache_manager, generate_cache_key

# Import SPARQL dependencies
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException, QueryCanceled, EndPointInternalError
from requests.exceptions import RequestException

# Custom exception for timeouts (defined in the data service layer)
class QueryTimeoutException(Exception):
    """Raised when a SPARQL query exceeds the execution time limit."""
    pass

logger = logging.getLogger(__name__)

class WikidataDataService:
    def __init__(self):
        # Initialize SPARQL client
        self.sparql = SPARQLWrapper(settings.SPARQL_SETTINGS['ENDPOINT_URL'])
        self.sparql.setReturnFormat(JSON)
        self.timeout = settings.SPARQL_SETTINGS['TIMEOUT_SECONDS']
        self.sparql.setTimeout(self.timeout)
        
        # Initialize Cache Manager
        self.cache_manager = get_cache_manager()

    def _execute_query(self, query: str) -> dict:
        """Internal helper to execute query with caching and exception handling."""
        cache_key = generate_cache_key(query)
        cached_result = self.cache_manager.get_result(cache_key)

        if cached_result:
            logger.info(f"Cache hit for key: {cache_key}")
            return cached_result
        
        try:
            self.sparql.setQuery(query)
            
            # Execute and check for timeout
            start_time = time.time()
            results = self.sparql.query().convert()
            execution_time = time.time() - start_time
            
            if execution_time > self.timeout:
                 # This path is primarily a fallback, as SPARQLWrapper should raise QueryCanceled
                 raise QueryTimeoutException(f"Query exceeded timeout of {self.timeout}s.")

            self.cache_manager.set_result(cache_key, results)
            logger.info(f"Cache miss. Query executed in {execution_time:.2f}s and cached.")
            return results

        except QueryCanceled as e:
            raise QueryTimeoutException(f"Query was canceled due to timeout: {e}")
        except SPARQLWrapperException as e:
            # Re-raise generic SPARQL errors (e.g., syntax errors, endpoint server issues)
            raise SPARQLWrapperException(f"SPARQL error: {e}")
        except RequestException as e:
            # Re-raise network errors (e.g., DNS failure, connection reset)
            raise RequestException(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}", exc_info=True)
            raise

    # --- Public Methods (search_entities, get_entity_properties, execute_custom_query) ---

    def execute_custom_query(self, query: str) -> dict:
        """Executes a user-defined SPARQL query."""
        # Simple query validation (avoids excessive resource usage)
        if not query.strip().upper().startswith('SELECT'):
            raise ValueError("Only SELECT queries are supported via this interface.")
            
        return self._execute_query(query)

    def get_entity_properties(self, entity_id: str, limit: int = 50) -> list:
        """
        Retrieves properties for a specific Wikidata entity.
        Includes BIND workaround for P1082/numerical literal bug.
        """
        # BIND trick is added to the query itself to handle the bug
        query = f"""
        SELECT ?property ?propertyLabel ?value ?valueLabel WHERE {{
          VALUES ?entity {{ wd:{entity_id} }}
          ?entity ?p ?value .
          ?property wikibase:directClaim ?p .
          
          SERVICE wikibase:label {{ 
             bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
             # 💡 FIX: The BIND trick to prevent the internal server error (P1082)
             BIND(IF(ISIRI(?value), ?value, "") AS ?valueLabel)
             ?property rdfs:label ?propertyLabel .
          }}
        }} LIMIT {limit}
        """
        results = self._execute_query(query)
        # ... (conversion logic to friendly dictionary format) ...
        return [] # Placeholder

    def search_entities(self, search_term: str, entity_type: str = 'item', limit: int = 10) -> list:
        """Searches for Wikidata entities by label."""
        # ... (SPARQL query construction for search) ...
        query = f"""
        SELECT ?entity ?entityLabel ?entityDescription WHERE {{
          SERVICE wikibase:mwapi {{
            bd:serviceParam wikibase:endpoint "www.wikidata.org";
                            wikibase:api "EntitySearch";
                            mwapi:search "{search_term}";
                            mwapi:language "en";
                            mwapi:limit "{limit}".
            ?entity wikibase:apiOutputItem mwapi:item.
          }}
          ?entity rdfs:label ?entityLabel .
          ?entity schema:description ?entityDescription .
          FILTER(LANG(?entityDescription) = "en")
        }}
        """
        results = self._execute_query(query)
        # ... (conversion logic) ...
        return [] # Placeholder

    def get_cache_stats(self) -> dict:
        """Returns cache statistics."""
        return self.cache_manager.get_cache_stats()

    def clear_cache(self) -> None:
        """Clears all entries from the cache."""
        self.cache_manager.invalidate_cache()