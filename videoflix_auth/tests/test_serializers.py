from django.test import TestCase
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from videoflix_auth.api.serializers import RegistrationSerializer


class RegistrationSerializerTestCase(TestCase):

    def setUp(self):
        self.valid_data = {
            "email": "testuser@example.com",
            "password": "Password1",
            "repeated_password": "Password1"
        }
        self.invalid_data_password_mismatch = {
            "email": "testuser@example.com",
            "password": "Password1",
            "repeated_password": "Password2"
        }
        self.invalid_data_weak_password = {
            "email": "testuser@example.com",
            "password": "password",
            "repeated_password": "password"
        }
        self.duplicate_email_data = {
            "email": "testuser@example.com",
            "password": "Password1",
            "repeated_password": "Password1"
        }

    def test_valid_data_creates_user(self):
      serializer = RegistrationSerializer(data=self.valid_data)
      self.assertTrue(serializer.is_valid(), msg=f"Serializer errors: {serializer.errors}")
      
      user = serializer.save()
      self.assertEqual(user.email, self.valid_data['email'], msg="Email mismatch")
      self.assertEqual(user.username, self.valid_data['email'], msg="Username should match email")
      self.assertFalse(user.is_active, msg="User should be inactive upon creation")

    def test_password_mismatch_raises_error(self):
        serializer = RegistrationSerializer(data=self.invalid_data_password_mismatch)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Passwords don't match", str(context.exception))

    def test_weak_password_raises_error(self):
        serializer = RegistrationSerializer(data=self.invalid_data_weak_password)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Min. 8 chars. Min. one uppercase letter and one number", str(context.exception))

    def test_duplicate_email_raises_error(self):
      User.objects.create_user(
          username=self.valid_data['email'], 
          email=self.valid_data['email'], 
          password="Password1"
      )
      
      serializer = RegistrationSerializer(data=self.duplicate_email_data)
      with self.assertRaises(ValidationError) as context:
          serializer.is_valid(raise_exception=True)
      self.assertIn("User with this email already exists", str(context.exception))