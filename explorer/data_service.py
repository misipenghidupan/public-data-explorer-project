"""
Refactored Data Service with MongoDB decoupling and SPARQL server bug workarounds
Implements native cache management and robust error handling
"""

import logging
import re
from typing import Dict, List, Any, Optional
from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException, EndPointInternalError
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

# Import our new cache manager
from .dal.cache_manager import get_cache_manager, generate_cache_key

logger = logging.getLogger(__name__)


class QueryTimeoutException(Exception):
    """Custom exception for SPARQL query timeouts."""
    pass


class WikidataDataService:
    """
    Enhanced data service with native MongoDB caching and robust error handling.
    Replaces djongo-based caching with direct PyMongo operations.
    """
    
    def __init__(self, endpoint_url: str = "https://query.wikidata.org/sparql"):
        self.endpoint_url = endpoint_url
        self.cache_manager = get_cache_manager()
        
        # Initialize SPARQL wrapper with aggressive timeout
        self.sparql = SPARQLWrapper(endpoint_url)
        self.sparql.setReturnFormat(JSON)
        self.sparql.setTimeout(20)  # 20-second timeout as mandated
        
        logger.info(f"WikidataDataService initialized with endpoint: {endpoint_url}")
    
    def _is_entity_variable(self, variable_name: str, query: str) -> bool:
        """
        Determine if a SPARQL variable represents a Wikidata entity (QID/PID).
        This helps avoid label service calls on literal values.
        
        Args:
            variable_name: SPARQL variable name (without ?)
            query: Full SPARQL query text
            
        Returns:
            True if variable likely represents an entity
        """
        # Look for patterns that indicate entity variables
        entity_patterns = [
            rf'\?{variable_name}\s+wdt:',  # Variable used as subject with property
            rf'wdt:\w+\s+\?{variable_name}',  # Variable used as object of property
            rf'\?{variable_name}\s+rdfs:label',  # Variable has label
            rf'wd:Q\d+\s+wdt:\w+\s+\?{variable_name}'  # Variable as object of entity property
        ]
        
        for pattern in entity_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        
        # Additional heuristic: if variable name suggests entity (common naming)
        entity_var_names = ['entity', 'item', 'property', 'subject', 'object']
        if any(name in variable_name.lower() for name in entity_var_names):
            return True
            
        return False
    
    def _enhance_query_with_labels(self, base_query: str) -> str:
        """
        Intelligently add label service to SPARQL query.
        Applies workaround for P1082 (Population) and similar numerical properties.
        
        Args:
            base_query: Original SPARQL query
            
        Returns:
            Enhanced query with selective label resolution
        """
        # Extract variables from SELECT clause
        select_match = re.search(r'SELECT\s+(.*?)\s+WHERE', base_query, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return base_query
        
        select_vars = select_match.group(1)
        
        # Find all variables in the query
        variables = re.findall(r'\?(\w+)', select_vars)
        
        if not variables:
            return base_query
        
        # Identify which variables are likely entities
        entity_variables = [var for var in variables if self._is_entity_variable(var, base_query)]
        
        if not entity_variables:
            return base_query
        
        # Build selective label service
        label_conditions = []
        for var in entity_variables:
            # Only apply label service to variables that are bound to entities
            label_conditions.append(f"""
            OPTIONAL {{
                BIND(IF(ISIRI(?{var}), ?{var}, ?unbound) AS ?{var}_entity)
                SERVICE wikibase:label {{ 
                    bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
                    ?{var}_entity rdfs:label ?{var}Label .
                }}
            }}""")
        
        # Insert label service before the closing brace
        enhanced_query = base_query.rstrip()
        if enhanced_query.endswith('}'):
            enhanced_query = enhanced_query[:-1]  # Remove closing brace
            enhanced_query += '\n'.join(label_conditions)
            enhanced_query += '\n}'
        
        logger.debug(f"Enhanced query with selective labels for variables: {entity_variables}")
        return enhanced_query
    
    def _execute_sparql_query(self, query: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Execute SPARQL query with robust error handling and caching.
        
        Args:
            query: SPARQL query string
            use_cache: Whether to use/update cache
            
        Returns:
            Query results dictionary
            
        Raises:
            QueryTimeoutException: When query exceeds timeout
            SPARQLWrapperException: For SPARQL-specific errors
            RequestException: For network errors
        """
        cache_key = generate_cache_key(query) if use_cache else None
        
        # Check cache first
        if use_cache and cache_key:
            cached_result = self.cache_manager.get_result(cache_key)
            if cached_result:
                logger.info("Returning cached result")
                return cached_result
        
        # Execute query
        try:
            self.sparql.setQuery(query)
            logger.info(f"Executing SPARQL query (timeout: 20s)")
            logger.debug(f"Query: {query[:200]}...")  # Log first 200 chars
            
            # Execute with timeout handling
            try:
                result = self.sparql.query().convert()
            except requests.exceptions.Timeout:
                raise QueryTimeoutException("SPARQL query exceeded 20-second timeout")
            except ConnectionError as e:
                raise RequestException(f"Connection error: {e}")
            
            # Cache successful results
            if use_cache and cache_key and result:
                self.cache_manager.set_result(cache_key, result)
                logger.debug("Result cached successfully")
            
            return result
            
        except EndPointInternalError as e:
            # Handle server-side errors (like P1082 numerical literal issue)
            logger.error(f"SPARQL endpoint internal error: {e}")
            raise SPARQLWrapperException(f"Wikidata server error: {e}")
        
        except SPARQLWrapperException as e:
            logger.error(f"SPARQL wrapper error: {e}")
            raise
        
        except RequestException as e:
            logger.error(f"Network error during SPARQL query: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Unexpected error during SPARQL query: {e}")
            raise SPARQLWrapperException(f"Unexpected error: {e}")
    
    def search_entities(self, search_term: str, entity_type: str = "item", 
                       limit: int = 10) -> List[Dict[str, str]]:
        """
        Search for Wikidata entities by name with enhanced error handling.
        
        Args:
            search_term: Search query
            entity_type: Type of entity ("item" or "property")
            limit: Maximum results to return
            
        Returns:
            List of entity dictionaries with id, label, description
            
        Raises:
            QueryTimeoutException: When search exceeds timeout
            SPARQLWrapperException: For SPARQL errors
        """
        # Escape search term for SPARQL
        escaped_term = search_term.replace('"', '\\"')
        
        query = f"""
        SELECT DISTINCT ?entity ?entityLabel ?entityDescription WHERE {{
            ?entity wikibase:label ?entityLabel .
            ?entity schema:description ?entityDescription .
            
            FILTER(LANG(?entityLabel) = "en" && LANG(?entityDescription) = "en")
            FILTER(CONTAINS(LCASE(?entityLabel), LCASE("{escaped_term}")))
            
            # Filter by entity type
            {"?entity wdt:P31 ?type ." if entity_type == "item" else ""}
        }}
        ORDER BY STRLEN(?entityLabel)
        LIMIT {limit}
        """
        
        try:
            results = self._execute_sparql_query(query)
            
            entities = []
            for binding in results.get('results', {}).get('bindings', []):
                entity_uri = binding.get('entity', {}).get('value', '')
                entity_id = entity_uri.split('/')[-1] if entity_uri else ''
                
                entities.append({
                    'id': entity_id,
                    'label': binding.get('entityLabel', {}).get('value', ''),
                    'description': binding.get('entityDescription', {}).get('value', '')
                })
            
            logger.info(f"Found {len(entities)} entities for search: {search_term}")
            return entities
            
        except (QueryTimeoutException, SPARQLWrapperException, RequestException) as e:
            logger.error(f"Error searching entities: {e}")
            raise
    
    def get_entity_properties(self, entity_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get properties for a specific entity with bug workarounds.
        
        Args:
            entity_id: Wikidata entity ID (e.g., "Q42")
            limit: Maximum properties to return
            
        Returns:
            List of property dictionaries
            
        Raises:
            QueryTimeoutException: When query exceeds timeout
            SPARQLWrapperException: For SPARQL errors
        """
        base_query = f"""
        SELECT DISTINCT ?property ?propertyLabel ?value WHERE {{
            wd:{entity_id} ?property ?value .
            ?prop wikibase:directClaim ?property .
            ?prop rdfs:label ?propertyLabel .
            FILTER(LANG(?propertyLabel) = "en")
        }}
        LIMIT {limit}
        """
        
        # Apply intelligent label enhancement
        enhanced_query = self._enhance_query_with_labels(base_query)
        
        try:
            results = self._execute_sparql_query(enhanced_query)
            
            properties = []
            for binding in results.get('results', {}).get('bindings', []):
                prop_uri = binding.get('property', {}).get('value', '')
                prop_id = prop_uri.split('/')[-1] if prop_uri else ''
                
                value_data = binding.get('value', {})
                value_type = value_data.get('type', 'literal')
                value_str = value_data.get('value', '')
                
                # Handle different value types appropriately
                if value_type == 'uri' and 'wikidata.org' in value_str:
                    value_display = value_str.split('/')[-1]  # Extract QID/PID
                else:
                    value_display = value_str
                
                properties.append({
                    'property_id': prop_id,
                    'property_label': binding.get('propertyLabel', {}).get('value', prop_id),
                    'value': value_display,
                    'value_type': value_type
                })
            
            logger.info(f"Retrieved {len(properties)} properties for {entity_id}")
            return properties
            
        except (QueryTimeoutException, SPARQLWrapperException, RequestException) as e:
            logger.error(f"Error getting properties for {entity_id}: {e}")
            raise
    
    def execute_custom_query(self, sparql_query: str) -> Dict[str, Any]:
        """
        Execute custom SPARQL query with all safety measures.
        
        Args:
            sparql_query: Custom SPARQL query
            
        Returns:
            Query results
            
        Raises:
            QueryTimeoutException: When query exceeds timeout
            SPARQLWrapperException: For SPARQL errors
        """
        try:
            # Apply bug workarounds if needed
            enhanced_query = self._enhance_query_with_labels(sparql_query)
            return self._execute_sparql_query(enhanced_query)
            
        except (QueryTimeoutException, SPARQLWrapperException, RequestException) as e:
            logger.error(f"Error executing custom query: {e}")
            raise
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring."""
        return self.cache_manager.get_cache_stats()
    
    def clear_cache(self):
        """Clear all cached results."""
        self.cache_manager.invalidate_cache()
        logger.info("Cache cleared by user request")