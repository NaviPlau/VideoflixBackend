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
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "User with this email already exists"})
      
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('repeated_password')
        validated_data['username'] = validated_data['email']
        user = User.objects.create_user(**validated_data)
        user.is_active = False 
        user.save()
        return user
    