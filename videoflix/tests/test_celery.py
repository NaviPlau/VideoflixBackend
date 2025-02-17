from django.test import TestCase
from unittest.mock import patch
from videoflix.celery import app

class CeleryConfigTestCase(TestCase):
    
    def test_celery_connection(self):
        """Test if Celery can connect to Redis broker."""
        try:
            app.broker_connection().connect()
            connected = True
        except Exception:
            connected = False
        
        self.assertTrue(connected, "Celery failed to connect to Redis.")

    @patch("videoflix.celery.app.broker_connection")
    def test_celery_connection_failure(self, mock_broker_connection):
        """Test if Celery handles connection failure properly."""
        
        mock_broker_connection().connect.side_effect = Exception("Forced Redis connection failure")

        try:
            exec(open("videoflix/celery.py").read())  
        except Exception:
            pass 
        with self.assertRaises(Exception) as context:
            app.broker_connection().connect()

        self.assertIn("Forced Redis connection failure", str(context.exception), "Exception message not triggered.")
