# Public Data Explorer (Wikidata SPARQL Client)

This project is a Django-based web application that allows users to write and execute SPARQL queries against the public Wikidata endpoint. It features real-time results display, query persistence (saving to a local SQLite database), and caching (using MongoDB) to improve performance for repeated queries.

## 🚀 Key Features

* **SPARQL Editor:** Write and execute complex queries against the official Wikidata endpoint.

* **MongoDB Caching:** Query results are cached for a Time-To-Live (TTL) period, significantly speeding up subsequent requests for the same data.

* **Persistence:** Saved queries are stored in a local SQLite database and are instantly accessible in the sidebar.

* **Responsive UI:** A modern, two-column interface built with Tailwind CSS.

## 🛠️ Setup and Installation

Follow these steps to get your local environment running.

### 1. Clone the Repository (Placeholder)

```

# Assuming you are cloning to your local machine

git clone \<your-repo-url\>
cd public-data-explorer-project

```

### 2. Create the Python Environment

Using the provided `environment.yml` file, create and activate the Conda environment:

```

conda env create -f environment.yml
conda activate wikidata-explorer

```

### 3. Database Setup

This project uses SQLite for saved queries and MongoDB for result caching.

**A. Configure MongoDB**
Ensure you have a MongoDB service running and update the following settings in your `data_explorer/settings.py` file:

```

# In data\_explorer/settings.py

MONGO\_CONNECTION\_STRING = "mongodb://localhost:27017/"
MONGO\_DATABASE\_NAME = "wikidata\_explorer\_new"

```

**B. Apply Migrations**
The Django `SavedQuery` model needs to be initialized:

```

python manage.py makemigrations explorer
python manage.py migrate

```

### 4. Run the Server

Start the Django development server:

```

python manage.py runserver 8001

```

The application will be accessible at `http://127.0.0.1:8001/`.

## ✍️ Usage

1. **Enter Query:** Paste a SPARQL query into the editor.

2. **Execute:** Click **"Execute Query"**. Results will appear in the **Table View** (default) or **Raw JSON** tab.

3. **Save:** Click **"Save Query"**, provide a title in the modal, and click Save. The query will appear in the left sidebar.

4. **Load:** Click any saved query in the sidebar to load it back into the editor.

## 💡 Example Working Query

Use this simple query to test connectivity and caching:

```

# Find a few basic properties of the Earth (Q2)
SELECT ?property ?propertyLabel ?value ?valueLabel WHERE {
  wd:Q2 ?property ?value.
  
  # Only select human-readable properties (statements)
  FILTER(STRSTARTS(STR(?property), "[http://www.wikidata.org/prop/direct/](http://www.wikidata.org/prop/direct/)"))
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 20
