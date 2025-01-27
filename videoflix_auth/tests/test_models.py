from django.test import TestCase
from django.contrib.auth.models import User
from videoflix_auth.models import PasswordResetToken 
from datetime import timedelta
from django.utils.timezone import now


class PasswordResetTokenModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="Password123"
        )
        self.token = PasswordResetToken.objects.create(
            user=self.user,
            token="testtoken1234567890"
        )

    def test_token_creation(self):
        """Test that a PasswordResetToken instance is created successfully."""
        self.assertEqual(self.token.user, self.user)
        self.assertEqual(self.token.token, "testtoken1234567890")
        self.assertTrue(self.token.created_at)

    def test_is_valid_within_15_minutes(self):
        """Test that is_valid() returns True within 15 minutes."""
        self.assertTrue(self.token.is_valid())

    def test_is_valid_after_15_minutes(self):
        """Test that is_valid() returns False after 15 minutes."""
        
        self.token.created_at = now() - timedelta(minutes=16)
        self.token.save()
        self.assertFalse(self.token.is_valid())

    def test_unique_token(self):
        """Test that the token field is unique."""
        with self.assertRaises(Exception):
            PasswordResetToken.objects.create(
                user=self.user,
                token="testtoken1234567890"
            )

    def test_token_user_relationship(self):
      """Test that deleting the user deletes the associated token."""
      
      user_id = self.user.id
      self.user.delete()
      tokens = PasswordResetToken.objects.filter(user_id=user_id)
      self.assertEqual(tokens.count(), 0)