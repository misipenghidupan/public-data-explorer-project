"""Refactored views with comprehensive error handling for the new data service."""

import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import time # Ensure 'time' is imported for api_status

# Import our refactored data service and custom exceptions
from .data_service import WikidataDataService, QueryTimeoutException
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

# --- View Functions (search_entities, entity_details, custom_query are approved) ---

def index(request):
    """Main landing page for the Wikidata Explorer."""
    return render(request, 'explorer/index.html')


def search_entities(request):
    """AJAX endpoint for entity search with comprehensive error handling."""
    # ... (Your robust search_entities implementation is approved) ...
    search_term = request.GET.get('q', '').strip()
    entity_type = request.GET.get('type', 'item')
    limit = min(int(request.GET.get('limit', 10)), 50)
    
    if not search_term:
        return JsonResponse({'error': 'Search term is required', 'entities': []})
    
    try:
        data_service = WikidataDataService()
        entities = data_service.search_entities(search_term=search_term, entity_type=entity_type, limit=limit)
        return JsonResponse({'entities': entities, 'search_term': search_term, 'count': len(entities)})
        
    except QueryTimeoutException as e:
        logger.warning(f"Search timeout for term '{search_term}': {e}")
        return JsonResponse({'error': 'Search timeout: The request took too long to process. Please try a more specific search term.', 'entities': [], 'timeout': True}, status=408)
        
    except SPARQLWrapperException as e:
        logger.error(f"SPARQL error during search for '{search_term}': {e}")
        return JsonResponse({'error': 'Search service temporarily unavailable. Please try again in a few moments.', 'entities': [], 'service_error': True}, status=503)
        
    except RequestException as e:
        logger.error(f"Network error during search for '{search_term}': {e}")
        return JsonResponse({'error': 'Network connection issue. Please check your connection and try again.', 'entities': [], 'network_error': True}, status=503)
        
    except Exception as e:
        logger.error(f"Unexpected error during search for '{search_term}': {e}", exc_info=True)
        return JsonResponse({'error': 'An unexpected error occurred. Please try again or contact support.', 'entities': []}, status=500)


def entity_details(request, entity_id):
    """Display detailed view of a specific entity with robust error handling."""
    # ... (Your robust entity_details implementation is approved) ...
    context = {'entity_id': entity_id, 'entity_label': entity_id, 'properties': [], 'error_message': None, 'cache_stats': None}
    try:
        data_service = WikidataDataService()
        properties = data_service.get_entity_properties(entity_id, limit=50)
        context.update({'properties': properties, 'property_count': len(properties), 'cache_stats': data_service.get_cache_stats()})
        for prop in properties:
            if prop.get('property_id') == 'P1476': 
                context['entity_label'] = prop.get('value', entity_id)
                break
        logger.info(f"Successfully loaded entity details for {entity_id}")
    except QueryTimeoutException:
        context['error_message'] = "Query Timeout: The Wikidata server took too long to respond."
    except SPARQLWrapperException:
        context['error_message'] = "Data Service Error: There was an issue retrieving data from Wikidata."
    except RequestException:
        context['error_message'] = "Connection Error: Unable to connect to the Wikidata service."
    except Exception as e:
        logger.error(f"Unexpected error loading entity {entity_id}: {e}", exc_info=True)
        context['error_message'] = "Unexpected Error: An unexpected error occurred while loading this entity."
    return render(request, 'explorer/results.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def custom_query(request):
    """Execute custom SPARQL query with comprehensive error handling."""
    # ... (Your robust custom_query implementation is approved) ...
    context = {'query_results': None, 'query_text': '', 'error_message': None, 'execution_time': None}
    try:
        sparql_query = json.loads(request.body).get('query', '') if request.content_type == 'application/json' else request.POST.get('query', '')
        if not sparql_query:
            context['error_message'] = "SPARQL query is required."
            return render(request, 'explorer/results.html', context)
        
        context['query_text'] = sparql_query
        start_time = time.time()
        data_service = WikidataDataService()
        results = data_service.execute_custom_query(sparql_query)
        execution_time = time.time() - start_time
        
        bindings = results.get('results', {}).get('bindings', [])
        context.update({'query_results': {'bindings': bindings, 'variables': results.get('head', {}).get('vars', []), 'count': len(bindings)}, 'execution_time': f"{execution_time:.2f}s", 'cache_stats': data_service.get_cache_stats()})
        logger.info(f"Custom query executed successfully in {execution_time:.2f}s")
        
    except QueryTimeoutException:
        context['error_message'] = "Query Timeout: Your SPARQL query took too long to execute (>20 seconds)."
    except SPARQLWrapperException:
        context['error_message'] = "SPARQL Error: There was an error in your query or the Wikidata service."
    except RequestException:
        context['error_message'] = "Network Error: Unable to execute your query due to connection issues."
    except json.JSONDecodeError:
        context['error_message'] = "Request Error: Invalid JSON data in request."
    except Exception as e:
        logger.error(f"Unexpected error in custom query: {e}", exc_info=True)
        context['error_message'] = "Unexpected Error: An unexpected error occurred while executing your query."
    
    return render(request, 'explorer/results.html', context)


# --- Corrected api_status and cache_management (No fragmentation) ---

def api_status(request):
    """API status endpoint for health monitoring."""
    try:
        data_service = WikidataDataService()
        cache_stats = data_service.get_cache_stats()
        
        # Simple connectivity check (no query needed)
        start_time = time.time()
        data_service.cache_manager.health_check() # Use DAL health check
        response_time = time.time() - start_time
        service_status = "healthy"
        
        return JsonResponse({
            'status': 'ok',
            'service_status': service_status,
            'response_time_ms': f"{response_time*1000:.2f}ms",
            'cache_stats': cache_stats,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return JsonResponse({
            'status': 'error',
            'error': f'Unable to check service status: {str(e)}',
            'timestamp': time.time()
        }, status=500)


def cache_management(request):
    """Cache management interface for monitoring and administration."""
    context = {'cache_stats': None, 'error_message': None, 'success_message': None}
    
    try:
        data_service = WikidataDataService()
        
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'clear_cache':
                data_service.clear_cache()
                context['success_message'] = "Cache cleared successfully."
                logger.info("Cache cleared via admin interface")
        
        context['cache_stats'] = data_service.get_cache_stats()
        
    except Exception as e:
        logger.error(f"Error in cache management interface: {e}", exc_info=True)
        context['error_message'] = (
            "Cache Management Error: Unable to access cache management functions. "
            "Check MongoDB connection and configuration."
        )
    
    return render(request, 'explorer/cache_management.html', context)