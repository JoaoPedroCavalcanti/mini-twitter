from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from rest_framework.validators import ValidationError
from utils.utils_functions import (
    hasAtLeast8Characters,
    hasSpecialCharacter,
    hasUpperCase,
)

from users.models import Profile


class ProfileSerializer(ModelSerializer):
    following = PrimaryKeyRelatedField(many=True, read_only=True)
    followers = PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'following', 'followers']
        read_only_fields = ['user']


User = get_user_model()

class UserSerializer(ModelSerializer):
    profile = ProfileSerializer(read_only=True)  # Mude para read_only

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'profile']
        read_only = ['id', 'profile']  # Mantenha o profile como read_only
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        User = get_user_model()
        
        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            password=validated_data.get('password'),
        )
        return user
    
    def validate_email(self, email):
        User = get_user_model()
        
        if User.objects.filter(email=email).exists():
            raise ValidationError('The provided email is already registered. Please choose another one.')

        return email  
    
    def validate_password(self, password):
        errors_list = []

        if not hasUpperCase(password):
            errors_list.append("Password must contain at least one uppercase letter.")
        
        if not hasAtLeast8Characters(password):
            errors_list.append("Password must be at least 8 characters long.")
            
        if not hasSpecialCharacter(password):
            errors_list.append("Password must have at least 1 special character(ex: !$%*<).")

        if errors_list:
            raise ValidationError(errors_list)

        return password