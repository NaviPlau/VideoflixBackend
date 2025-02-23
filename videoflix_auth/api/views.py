from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from .serializers import RegistrationSerializer
from .utils import send_welcome_email, send_password_reset_email
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
import uuid
from django.contrib.auth.models import User
from videoflix_auth.models import PasswordResetToken
from videoflix_videos.models import UserVideoProgress


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Register a new user.
        This API endpoint takes a POST request with the following fields:
        - email (string): The email address of the user.
        - password (string): The password to use for the user.
        - repeated_password (string): The repeated password to check against the password.
        Returns a JSON response with the following keys:
        - message (string): A message indicating that the user was registered successfully.
        - user_id (int): The ID of the user that was just registered.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))  
            token = default_token_generator.make_token(user)  
            send_welcome_email(
                user_email=user.email,
                user_name=user.username,
                activation_link=f"https://videoflix.paul-ivan.com/activate-account/{uid}/{token}/"
            )
            return Response({
                'message': 'You registered successfully',
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccountView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, uidb64, token, *args, **kwargs):
        """
        Activate a user's account using the activation link.

        This API endpoint takes a GET request with the following parameters:
        - uidb64 (string): The base64-encoded user ID.
        - token (string): The activation token.

        Returns a JSON response with the following keys:
        - message (string): A message indicating that the account was activated successfully.
        - error (string): An error message if the activation link is invalid or has expired, or if the user is invalid.

        The endpoint returns HTTP 200 if the account is activated successfully, and HTTP 400 if there is an error.
        """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.is_active = True 
                user.save()
                return Response({"message": "Account activated successfully! You can now log in."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Activation link is invalid or has expired."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Invalid user."}, status=status.HTTP_400_BAD_REQUEST)
        
        
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Authenticate a user using email and password.
        """
        username = request.data.get('email')  
        password = request.data.get('password')

        try:
            user = User.objects.get(username=username)

            if not user.check_password(password):
                return Response({"message": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)

            if not user.is_active:
                return Response({"message": "You still didn't activate your account."}, status=status.HTTP_403_FORBIDDEN)

            # Check if the user is the guest account
            if user.email == "guest.videoflix@gmail.com":
                self.reset_guest_progress(user)

            token, _ = Token.objects.get_or_create(user=user)

            return Response(
                {"id": user.id, "username": user.username, "token": token.key},
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response({"message": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)

    def reset_guest_progress(self, user):
        """
        Resets the progress of all videos for the guest user.
        """
        UserVideoProgress.objects.filter(user=user).update(last_viewed_position=0.0, viewed=False)


class TokenLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        """
        Authenticate a user using the authentication token.

        This API endpoint takes a POST request with the following field:
        - token (string): The authentication token of the user.

        Returns a JSON response with the following keys:
        - id (int): The ID of the user.
        - email (string): The email address of the user.
        - token (string): The authentication token of the user.

        The endpoint returns HTTP 200 if the authentication is successful, and HTTP 401 if the token is invalid.
        """
        token = request.data.get('token')
        try:
            user = Token.objects.get(key=token).user
            return Response(
                {  "id": user.id, "email": user.email, "token": token }, status=status.HTTP_200_OK
            )
        except Token.DoesNotExist:  
            return Response(
                {"message": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED
        )
        
        
class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Send a password reset email to the user.

        This API endpoint takes a POST request with the following field:
        - email (string): The email address of the user.

        Returns a JSON response with the following key:
        - message (string): A message indicating that the password reset email was sent successfully.

        The endpoint returns HTTP 200 if the email is sent successfully.
        """
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            token = str(uuid.uuid4()) 
            PasswordResetToken.objects.create(user=user, token=token)
            reset_link = f"https://videoflix.paul-ivan.com/reset-password/confirm/{token}/"
            send_password_reset_email(
                user_email=user.email,
                user_name=user.username,
                reset_link=reset_link
            )
            return Response({'message': 'Password reset email sent successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Password reset email sent successfully'}, status=status.HTTP_200_OK)  
        
        
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Confirm and set a new password for the user using a password reset token.

        This API endpoint takes a POST request with the following fields:
        - password (string): The new password for the user.
        - repeated_password (string): The repeated password for confirmation.

        The endpoint checks if the provided token is valid and not expired, 
        then sets the new password for the user if the token is valid and 
        both password fields match.

        Returns a JSON response with the following keys:
        - message (string): A message indicating that the password was reset successfully.
        - error (string): An error message if the token is invalid or expired, or if 
        the password fields are missing or do not match.

        The endpoint returns HTTP 200 if the password is reset successfully, and HTTP 400 
        if there is an error.
        """

        token = kwargs.get('token')
        password = request.data.get('password')
        repeated_password = request.data.get('repeated_password')
        if not password or not repeated_password:
            return Response({'error': 'Both password fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        if password != repeated_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            if not reset_token.is_valid():
                return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
            user = reset_token.user
            user.set_password(password)
            user.save()
            reset_token.delete()
            return Response({'message': 'Password reset successfully!'}, status=status.HTTP_200_OK)
        except PasswordResetToken.DoesNotExist:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
