🌐 Django Data Explorer (MongoDB/SPARQL)
Version: beta-1.1.0

This project is a Django web application designed to explore public data (via a SPARQL endpoint) using MongoDB as the primary database backend and a robust Conda environment for dependency management.

🚀 Features
MongoDB Backend: Uses djongo to enable the standard Django ORM, authentication, and sessions with MongoDB.

Data Exploration: Communicates with external SPARQL endpoints using SPARQLWrapper.

Custom Caching: Implements a high-performance caching layer using raw pymongo for SPARQL query results.

Secure Configuration: Uses python-decouple to manage sensitive settings via a local .env file.

Isolated Environment: Managed by Conda to ensure specific Python and package versions are maintained.

⚙️ Prerequisites
Before running the project, ensure you have the following installed:

Git

Miniconda or Anaconda (recommended for environment management)

MongoDB Server (running locally or a connection string from MongoDB Atlas)

📦 Project Setup
Follow these steps to clone the repository and set up your isolated Conda environment.

1. Clone Repository
Bash

git clone <YOUR_REPOSITORY_URL> public-data-explorer-project
cd public-data-explorer-project
2. Create and Activate Conda Environment
We use the provided environment.yml to recreate the exact environment, including the compatible Python 3.11 version.

Bash

# Create the environment using the YAML file
conda env create -f environment.yml

# Activate the newly created environment (important!)
conda activate ./conda_env
3. Install Pip-Only Dependencies
Some packages, like djongo, are installed via pip within the active Conda environment.

Bash

pip install -r requirements.txt
4. Configure Environment Variables
Create a file named .env in the root directory and add your connection strings and secrets.

Bash

# .env file example
SECRET_KEY='your-secret-key-here'

# MongoDB Connection Details
# Use a full connection string (e.g., from MongoDB Atlas or local server)
MONGO_URI='mongodb://<USER>:<PASSWORD>@<HOST>:<PORT>/'
MONGO_DATABASE='data_explorer_db'

# Optional: Set connection details for a specific SPARQL endpoint if needed
SPARQL_ENDPOINT='http://dbpedia.org/sparql'
🏃 Running the Application
1. Run Migrations
Apply Django's initial migrations to your MongoDB instance. This creates the necessary core collections (auth_user, django_session, __schema__).

Bash

python manage.py migrate
2. Create Superuser (Optional)
Create an admin user to access the Django Administration panel.

Bash

python manage.py createsuperuser
3. Start the Server
Bash

python manage.py runserver
The application will be accessible at http://127.0.0.1:8000/.

🧩 Key Technologies
Technology	Role
Python 3.11	Runtime Environment (Conda controlled)
Django 4.2.11	Web Framework (LTS version)
Djongo	ORM Connector (Django ➡️ MongoDB)
PyMongo	Native MongoDB Driver (Used for custom cache)
SPARQLWrapper	SPARQL Query Client
Conda	Environment and Dependency Manager
python-decouple	Configuration/Secret Management

Export to Sheets
🤝 Contribution
If you plan to scale this project, consider using the environment.yml file for precise environment recreation and ensuring any new dependencies are added to both requirements.txt and the environment.yml (via pip freeze and conda env export).

© 2025 [Your Name/Company Name]
