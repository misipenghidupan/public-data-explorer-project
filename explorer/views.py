from django.shortcuts import render
from django.views import View
from .explorer_service import ExplorerService

class DataExplorerView(View):
    """
    Main view for the data explorer.
    Handles GET requests for the initial page load and POST requests for query submission.
    """
    template_name = 'explorer/data_explorer.html'
    
    def get(self, request):
        """Renders the initial data explorer page."""
        context = self._get_default_context()
        return render(request, self.template_name, context)

    def post(self, request):
        """Processes the submitted query form."""
        
        # Determine the query type from the submission
        query_type = request.POST.get('query_type')
        
        # Initialize variables
        identifier = None
        query_input = None
        
        if query_type == 'qid':
            identifier = request.POST.get('qid_input', '').strip()
            query_input = request.POST.get('properties_input', '').strip()
        elif query_type == 'sparql':
            query_input = request.POST.get('sparql_query_input', '').strip()
        
        # Execute the query via the service layer
        service = ExplorerService()
        head_vars, results, is_db_connected, error_message = service.execute_query(
            query_type=query_type,
            identifier=identifier,
            query_input=query_input
        )
        
        # Prepare context for template
        context = {
            'head_vars': head_vars,
            'results': results,
            'error_message': error_message,
            'is_db_connected': is_db_connected,
            'query_type': query_type,
            'qid_input': identifier if query_type == 'qid' else '',
            'properties_input': query_input if query_type == 'qid' else '',
            'sparql_query_input': query_input if query_type == 'sparql' else '',
        }
        
        return render(request, self.template_name, context)

    def _get_default_context(self):
        """Provides default context for the initial GET request."""
        service = ExplorerService()
        return {
            'head_vars': [],
            'results': [],
            'error_message': None,
            'is_db_connected': service.data_service.is_db_connected,
            'query_type': 'qid', # Default to QID view
            'qid_input': 'Q30',
            'properties_input': 'P31,P1082,P6',
            'sparql_query_input': 'SELECT ?item ?itemLabel WHERE { ?item wdt:P31 wd:Q5 . SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" . } } LIMIT 10',
        }