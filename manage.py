#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    
    # Define the correct settings module path for this project.
    correct_settings_module = 'data_explorer.settings'
    
    # Check if DJANGO_SETTINGS_MODULE is currently set to the correct value.
    # If it is not correct, or not set at all, we force it to the correct value.
    if os.environ.get('DJANGO_SETTINGS_MODULE') != correct_settings_module:
        os.environ['DJANGO_SETTINGS_MODULE'] = correct_settings_module
        
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
