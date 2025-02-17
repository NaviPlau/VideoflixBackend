import os
import pytest
from importlib import import_module
from django.core.asgi import get_asgi_application

def test_asgi_application_loads():
    """Test if ASGI application loads and is callable."""
    
    # Ensure settings module is set correctly
    assert os.getenv("DJANGO_SETTINGS_MODULE") == "videoflix.settings", "DJANGO_SETTINGS_MODULE is incorrect"

    try:
        # Import the ASGI application explicitly
        asgi_module = import_module("videoflix.asgi")
        application = asgi_module.application  # Access the application instance

        assert application is not None, "ASGI application is None"
        assert callable(application), "ASGI application is not callable"

    except Exception as e:
        pytest.fail(f"ASGI application failed to load: {str(e)}")
