from rest_framework.serializers import ModelSerializer

from posts.models import PostModel


class PostSerializer(ModelSerializer):
    class Meta:
        model = PostModel
        fields = ['id', 'poster_user', 'text_content', 'image', 'likes_counter','liked_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'poster_user': {'required': False},
            'text_content': {'required': True},
            'image': {'required': False},
            'likes_counter': {'required': False},
            'liked_by': {'required': False},
            }
        
    # Recieve the user from the view
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)

    # Adding the user to poster_user automattically
    def validate(self, attrs):
        attrs['poster_user'] = self.user
        return super().validate(attrs)