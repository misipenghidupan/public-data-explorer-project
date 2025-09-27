import json
import requests
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from .cache_manager import MongoCacheManager
from .models import SavedQuery

# Initialize the cache manager instance once on module load
try:
    cache_manager = MongoCacheManager()
except Exception as e:
    # This should be logged for debugging, but we allow the app to run without the cache manager
    # if the connection fails, as long as Django's check passes.
    print(f"Failed to initialize MongoCacheManager: {e}")
    cache_manager = None

def explorer_view(request):
    """
    Renders the main explorer interface.
    """
    # Load all saved queries to populate the sidebar in the new UI
    saved_queries = SavedQuery.objects.all().order_by('-created_at')
    
    context = {
        'SPARQL_ENDPOINT': settings.SPARQL_ENDPOINT,
        'saved_queries': [model_to_dict(q) for q in saved_queries]
    }
    # This now correctly renders the refined UI template
    return render(request, 'explorer/index.html', context)

@csrf_exempt
def execute_query(request):
    """
    Handles the execution of a SPARQL query, checking the cache first.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query')
            
            if not query:
                return HttpResponseBadRequest("Query parameter is missing.")

            # 1. Check Cache
            if cache_manager:
                cached_result = cache_manager.get(query)
                if cached_result:
                    return JsonResponse(cached_result)

            # 2. Execute Query
            headers = {'Accept': 'application/json'}
            params = {'query': query}
            
            response = requests.get(settings.SPARQL_ENDPOINT, params=params, headers=headers)
            response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
            
            result = response.json()

            # 3. Save to Cache
            if cache_manager:
                cache_manager.set(query, result)

            return JsonResponse(result)

        except requests.exceptions.HTTPError as e:
            return JsonResponse({'error': f"SPARQL Endpoint Error: {e.response.status_code} {e.response.text}"}, status=500)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': f"Network or connection error: {e}"}, status=500)
        except json.JSONDecodeError:
            return JsonResponse({'error': "Invalid JSON in request body."}, status=400)
        except Exception as e:
            return JsonResponse({'error': f"An internal server error occurred: {e}"}, status=500)
            
    return HttpResponseBadRequest("Invalid request method.")

@csrf_exempt
def save_query(request):
    """
    Saves a query (title and query text) to the SQLite database.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            query_text = data.get('query')

            if not title or not query_text:
                return HttpResponseBadRequest("Title or query is missing.")

            saved_query = SavedQuery.objects.create(title=title, query=query_text)
            
            return JsonResponse(model_to_dict(saved_query), status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': "Invalid JSON in request body."}, status=400)
        except Exception as e:
            return JsonResponse({'error': f"Failed to save query: {e}"}, status=500)

    return HttpResponseBadRequest("Invalid request method.")

def list_queries(request):
    """
    Returns a JSON list of all saved queries for dynamic sidebar updates.
    """
    if request.method == 'GET':
        try:
            saved_queries = SavedQuery.objects.all().order_by('-created_at')
            queries_list = [model_to_dict(q) for q in saved_queries]
            return JsonResponse(queries_list, safe=False)
        except Exception as e:
            return JsonResponse({'error': f"Failed to load queries: {e}"}, status=500)
    
    return HttpResponseBadRequest("Invalid request method.")
