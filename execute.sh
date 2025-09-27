#!/bin/bash
# 1. Deactivate the current environment (optional, but safest)
# conda deactivate

# 2. Reactivate the environment
# conda activate wikidata-explorer

# 3. Uninstall the current (likely corrupted) package
pip uninstall python-decouple -y
pip uninstall decouple -y 
# Note: The package is called 'python-decouple', but sometimes the alias 'decouple' is needed.

# 4. Install the package again, ensuring no confusion
pip install python-decouple

# 5. After successful installation, restart your IDE/editor.