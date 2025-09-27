# 🌐 Wikidata Explorer: The Semantic Web Query Tool (beta-2.0.0)

A powerful, stable, and highly performant web application for exploring the Wikidata knowledge graph using SPARQL. This **beta-2.0.0** release marks a major architectural refactoring, eliminating legacy dependencies and introducing native caching and robust error handling.

## 🚀 Architectural Highlights (Beta 2.0.0)

This release focuses entirely on stability, performance, and maintainability.

- **Framework Upgrade:** Fully migrated to **Django 5.1.4 LTS**.
- **Data Access Layer (DAL):** Complete removal of `djongo`. Switched to native **PyMongo 4.10.1** for all SPARQL result caching, ensuring decoupling and performance.
- **Reliability:** Implemented a mandatory **20-second timeout** on all Wikidata SPARQL queries to prevent resource exhaustion.
- **Bug Fix:** Integrated an intelligent `BIND` workaround in the Data Service to resolve the long-standing Wikidata server error when querying numerical literals (e.g., P1082 Population) alongside labels.
- **Resilience:** Comprehensive presentation-layer error handling for network errors, timeouts, and server-side SPARQL errors, ensuring graceful degradation and user-friendly messages.
- **Caching:** SPARQL results are cached in MongoDB with automatic **TTL (Time-To-Live) indexing** for expiration control.

## 🛠️ Setup and Installation

### 1. Prerequisites

- **Python 3.12.9**
- **Conda** (Recommended for environment management)
- **MongoDB** (Running instance accessible via `mongodb://localhost:27017/` by default)

### 2. Environment Setup

Use the provided `environment.yml` to create and activate the project environment.

```bash
# Create and activate the new environment
conda env create -f environment.yml
conda activate wikidata-explorer

# Install required pip packages
pip install -r requirements.txt # Assuming pip dependencies are specified here
````

### 3\. Configuration (`.env` or Environment Variables)

The application relies on specific environment variables for configuration. Create a `.env` file in the project root based on this template:

```ini
# Core Django Settings
DJANGO_SECRET_KEY='your-strong-secret-key-here'
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# MongoDB Cache Configuration
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/
MONGODB_DATABASE=wikidata_explorer
MONGODB_CACHE_COLLECTION=sparql_cache
MONGODB_CACHE_TTL=3600 # Cache expiration in seconds (1 hour)

# SPARQL Service Settings
SPARQL_ENDPOINT=[https://query.wikidata.org/sparql](https://query.wikidata.org/sparql)
SPARQL_TIMEOUT=20 # MANDATORY: 20-second query timeout
```

### 4\. Database Setup and Run

Run the standard Django setup commands:

```bash
# Apply Django migrations (for SQLite/auth/sessions)
python manage.py migrate

# Create a superuser to access the admin interface (Optional)
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

The application will be accessible at `http://127.0.0.1:8000/`.

## 🧪 Verification and Testing

To ensure the new architecture is functioning correctly, verify these endpoints:

1.  **Cache/Health Status:**

      * **Endpoint:** `/api/status/`
      * **Check:** Verify the JSON response contains the `cache_stats` block, confirming native MongoDB connection and TTL configuration.

2.  **Timeout Handling:**

      * Execute a known slow query (or one that hits the 20-second limit).
      * **Check:** The application must return a user-friendly "Query Timeout" message (HTTP 408 or rendered error template) and log a `QueryTimeoutException`.

3.  **Bug Workaround:**

      * Use the entity detail page or custom query to retrieve properties that include `wdt:P1082` (Population) alongside `rdfs:label`.
      * **Check:** The query should succeed without raising a `SPARQLWrapper.SPARQLExceptions.EndPointInternalError`.

## 🧑‍💻 Contribution

The `beta-2.0.0` branch is considered stable for testing. All new features or fixes should be targeted toward the current stable branch.

**Maintainers:** [Your Name/Team]
**License:** [Your License]
