from rest_framework import serializers

from posts.models import PostModel


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostModel
        fields = [
            "id",
            "poster_user",
            "text_content",
            "image",
            "likes_counter",
            "liked_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "poster_user",
            "likes_counter",
            "liked_by",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    # Define valores automaticamente ao criar o post
    def create(self, validated_data):
        validated_data["poster_user"] = self.user
        validated_data["likes_counter"] = 0
        validated_data["liked_by"] = []
        return super().create(validated_data)


class LikeSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()


class DislikeSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()
