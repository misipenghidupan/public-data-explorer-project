from .data_service import DataService

class ExplorerService:
    """
    The service layer that coordinates between the view and the data layer.
    It contains the business logic for the data explorer.
    """
    
    def __init__(self):
        """Initializes the DataService dependency."""
        self.data_service = DataService()

    def generate_sparql_query(self, qid, properties_str):
        """
        Generates a basic SPARQL query to retrieve properties for a given QID.
        :param qid: The Wikidata QID (e.g., 'Q30' for USA).
        :param properties_str: Comma-separated string of property IDs (e.g., 'P31,P1082').
        :return: A complete SPARQL query string.
        """
        if not qid or not properties_str:
            raise ValueError("QID and Properties are required for QID query generation.")

        qid = qid.strip().upper()
        # Basic check for QID format
        if not qid.startswith('Q') or not qid[1:].isdigit():
             raise ValueError("QID must start with 'Q' followed by digits.")

        properties = [p.strip().upper() for p in properties_str.split(',') if p.strip()]
        
        select_vars = [f'?{p}' for p in properties]
        where_clauses = [f'wd:{qid} wdt:{p} ?{p} .' for p in properties]
        
        select_line = " ".join(select_vars)
        where_block = "\n    ".join(where_clauses)

        sparql_query = f"""
SELECT DISTINCT ?itemLabel {select_line} 
WHERE {{
    VALUES ?item {{ wd:{qid} }}
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" . ?item rdfs:label ?itemLabel . }}
    {where_block}
}}
LIMIT 100
"""
        return sparql_query.strip()


    def execute_query(self, query_type, identifier, query_input):
        """
        Executes a query based on the type (SPARQL or QID/Property).
        :param query_type: 'sparql' or 'qid'
        :param identifier: QID for 'qid' type (ignored for 'sparql')
        :param query_input: SPARQL query string or property string for 'qid' type
        :return: Tuple (head_vars, results, is_db_connected, error_message)
        """
        
        is_db_connected = self.data_service.is_db_connected
        error_message = None
        head_vars = []
        results = []
        sparql_query = None

        try:
            if query_type == 'qid':
                sparql_query = self.generate_sparql_query(identifier, query_input)
            elif query_type == 'sparql':
                sparql_query = query_input
            else:
                raise ValueError("Invalid query_type specified.")

            # Execute the SPARQL query
            head_vars, results = self.data_service.execute_sparql_query(sparql_query)

        except ValueError as e:
            error_message = f"Input Error: {e}"
        except RuntimeError as e:
            error_message = f"Query Execution Error: {e}. Check server logs for details."
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"

        return head_vars, results, is_db_connected, error_message