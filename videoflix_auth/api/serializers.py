from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    password = serializers.CharField(
        write_only=True,
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$',
                message="Min. 8 chars. Min. one uppercase letter and one number"
            )
        ]
    )
    
    class Meta:
        model = User
        fields = ('email', 'password', 'repeated_password')
    
    def validate(self, data):
        """
        Validate the registration data.

        This method checks if the provided email is already registered 
        and ensures that the password and repeated password match.

        Args:
            data (dict): The registration data containing 'email', 
                        'password', and 'repeated_password'.

        Raises:
            serializers.ValidationError: If the email already exists 
                                        or if the passwords do not match.

        Returns:
            dict: The validated data.
        """

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "User with this email already exists"})
      
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return data
    
    def create(self, validated_data):
        """
        Create a new user with the validated data.

        This method takes the validated registration data, removes the repeated
        password, sets the username to the email, and creates a new user with
        the remaining data. The user is set to inactive and saved.

        Args:
            validated_data (dict): The validated registration data

        Returns:
            User: The newly created user
        """
        validated_data.pop('repeated_password')
        validated_data['username'] = validated_data['email']
        user = User.objects.create_user(**validated_data)
        user.is_active = False 
        user.save()
        return user
    