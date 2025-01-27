from unittest.mock import patch
from django.test import TestCase, override_settings
from videoflix_auth.api.utils import send_welcome_email, send_password_reset_email

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EmailUtilsTestCase(TestCase):
    def setUp(self):
        self.user_email = "testuser@example.com"
        self.user_name = "Test User"
        self.activation_link = "http://example.com/activate?token=123"
        self.reset_link = "http://example.com/reset?token=456"

    @patch('videoflix_auth.api.utils.EmailMultiAlternatives.send')
    def test_send_welcome_email(self, mock_send):
        send_welcome_email(self.user_email, self.user_name, self.activation_link)
        mock_send.assert_called_once()

    @patch('videoflix_auth.api.utils.EmailMultiAlternatives.send')
    def test_send_password_reset_email(self, mock_send):
        send_password_reset_email(self.user_email, self.user_name, self.reset_link)
        mock_send.assert_called_once()