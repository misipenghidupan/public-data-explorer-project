# Public Data Explorer (Django / Wikidata SPARQL)

🛡️ **Version:** beta-1.1.0 | 🐍 **Python:** 3.11 | 🌐 **Framework:** Django **4.2.11**

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

  * **Conda** (Miniconda or Anaconda)
  * **Git**
  * **MongoDB Server** (running and accessible)

### Step 1: Clone and Activate Conda Environment

We use Conda's prefix method to create an isolated environment locally within the project directory.

```bash
# 1. Clone the repository
git clone [https://github.com/YourUsername/public-data-explorer.git](https://github.com/YourUsername/public-data-explorer.git)
cd public-data-explorer-project

# 2. Create and activate the Conda environment using the lock file
conda env create -f environment.yml --prefix ./conda_env

# 3. Activate the new local environment
conda activate ./conda_env
