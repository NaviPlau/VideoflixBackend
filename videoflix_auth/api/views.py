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


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))  
            token = default_token_generator.make_token(user)  
            send_welcome_email(
                user_email=user.email,
                user_name=user.username,
                activation_link=f"http://localhost:4200/activate-account/{uid}/{token}/"
            )
            return Response({
                'message': 'You registered successfully',
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccountView(APIView):
    def get(self, request, uidb64, token, *args, **kwargs):
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
        username = request.data.get('email')  
        password = request.data.get('password')
        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                return Response( {"message": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)
            if not user.is_active:
                return Response( {"message": "You still didn't activate your account."}, status=status.HTTP_403_FORBIDDEN)
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {  "id": user.id, "username": user.username, "token": token.key }, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response( {"message": "Invalid username or password."},  status=status.HTTP_401_UNAUTHORIZED )


class TokenLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
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
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            token = str(uuid.uuid4()) 
            PasswordResetToken.objects.create(user=user, token=token)
            reset_link = f"http://localhost:4200/reset-password/confirm/{token}/"
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