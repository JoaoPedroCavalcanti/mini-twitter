from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model
from rest_framework.validators import ValidationError

class UserSerializer(ModelSerializer):
    
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'password']
        read_only = ['id']
        extra_kwargs = {
            'username': {'required': True},
            'password': {'write_only': True, 'required': True},
            'email': {'required': True},
        }
        
    def create(self, validated_data):
        User = get_user_model()
        
        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),  # Certifique-se de que o e-mail está sendo atribuído
            password=validated_data.get('password'),
        )
        return user
    
    def validate_email(self, email):
        User = get_user_model()
        
        if User.objects.filter(email=email).exists():
            raise ValidationError('The provided email is already registered. Please choose another one.')

        return email  