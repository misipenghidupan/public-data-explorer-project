# Public Data Explorer (Django / Wikidata SPARQL)

🛡️ **Version:** 1.0.0 | 🐍 **Python:** 3.8+ | 🌐 **Framework:** Django

A robust web application designed to query and explore public data from **Wikidata's SPARQL endpoint**. This project utilizes a **Service Layer architecture** and implements a **Time-To-Live (TTL) caching mechanism** using MongoDB for performance optimization.

## 🌟 Features

  * **Dual Query Interface:** Seamlessly switch between **QID/Property Lookup** (for quick exploration) and **Raw SPARQL Query** (for advanced users).
  * **Intelligent Caching:** Implements a **24-Hour TTL cache** via **PyMongo**, reducing latency and load on the external Wikidata API for repeated queries.
  * **Dynamic Results:** The frontend renders columns and rows entirely dynamically based on the variables returned by the SPARQL query (using a custom Django template filter).
  * **Service Layer Separation:** Clean separation of concerns between Views, Business Logic, and Data Access (`data_service.py` handles PyMongo and SPARQLWrapper).

-----

## 🏗️ Architecture

The project adheres to a Service Layer pattern for maintainability and testability.

| Component | Technology | Responsibility |
| :--- | :--- | :--- |
| **View Layer** (`views.py`) | Django Views | Handles HTTP requests, calls the Service Layer, and manages template context. |
| **Service Layer** (`explorer_service.py`) | Python | Business Logic: Transforms QID/Property input into SPARQL queries. Coordinates with the Data Layer. |
| **Data Layer** (`data_service.py`) | PyMongo, SPARQLWrapper | External Access: Manages MongoDB caching (TTL Index) and executes external SPARQL queries. |
| **Frontend** (`data_explorer.html`) | HTML, Django Templates | Dynamic Rendering: Uses `{{ row|get_item:col }}` to iterate and display variable-driven results. |

-----

## ⚙️ Local Setup and Installation

### Prerequisites

You must have the following installed and running:

  * **Python** (3.8 or higher)
  * **MongoDB Server** (running and accessible)

### Step 1: Clone and Activate

```bash
# 1. Clone the repository
git clone https://github.com/YourUsername/public-data-explorer.git
cd public-data-explorer-project

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install Django python-decouple pymongo SPARQLWrapper requests
```

### Step 3: Configure Environment (`.env`)

Create a **`.env`** file in the project root directory and add the following configuration variables. This is crucial for security and database connectivity.

```ini
# .env
SECRET_KEY=your-django-secret-key-here
DEBUG=True

# MongoDB Connection
# IMPORTANT: Ensure this URI matches your running MongoDB instance
MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE=public_data_explorer
MONGO_COLLECTION_CACHE=sparql_cache
```

### Step 4: Run the Application

```bash
# Apply Django migrations (for internal auth/admin tables)
python manage.py migrate

# Start the Django development server
python manage.py runserver
```

The application will now be running at `http://127.0.0.1:8000/`.

-----

## 🚀 Usage

Access the application in your browser and check the **MongoDB Cache Status** in the top right corner. It should report **"Connected ✅"** if your `.env` and MongoDB server are correctly configured.

### A. QID & Property Lookup Example

This is the recommended starting point for basic exploration.

| Field | Example Input | Description |
| :--- | :--- | :--- |
| **Wikidata QID** | `Q30` | Target entity (e.g., United States of America). |
| **Property IDs** | `P31,P1082,P6` | Properties to retrieve (e.g., instance of, population, head of government). |

### B. Raw SPARQL Query Example

For advanced queries and aggregates.

```sparql
SELECT ?item ?itemLabel WHERE {
  ?item wdt:P31 wd:Q5 . 
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" . } 
} 
LIMIT 10
```

### Cache Management

  * When a query is executed for the first time, `data_service.py` stores the result in MongoDB with a timestamp.
  * MongoDB's built-in **TTL index** on the `sparql_cache` collection automatically handles the deletion of documents older than 24 hours.
  * Subsequent identical queries retrieve data from the cache, resulting in **significantly faster load times**.

-----

## 🤝 Contributing

Contributions are welcome\! Please open an issue or submit a pull request for any bug fixes, feature additions, or improvements to the documentation.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

-----

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

-----

## 👤 Author

  * **[Your Name / GitHub Username]** - *Developer*
      * [Link to your portfolio or LinkedIn (Optional)]