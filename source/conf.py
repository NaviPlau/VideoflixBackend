import os
import sys
import django

# Set the correct path to your Django project root
sys.path.insert(0, os.path.abspath('../'))  # Adjust this if needed

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'videoflix.settings')

# Initialize Django before importing models
django.setup()


extensions = [
    'sphinx.ext.autodoc',   # Automatically extract docstrings
    'sphinx.ext.napoleon',  # Support for Google-style and NumPy-style docstrings
    'sphinx.ext.viewcode',  # Add links to source code
]
