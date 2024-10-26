from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.viewsets import ModelViewSet

from posts.models import PostModel
from posts.serializers import PostSerializer


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    queryset = PostModel.objects.all().order_by("-created_at")
    permission_classes = [
        IsAuthenticated,
    ]

    # Send user to serializer
    def get_serializer(self, *args, **kwargs):
        kwargs["user"] = self.request.user
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        if not self.request.user.is_staff:  # type: ignore
            return PostModel.objects.filter(poster_user=self.request.user.id)  # type: ignore
        return super().get_queryset()

    def check_post_permissions(self, post):
        if self.request.user.id != post.poster_user.id:  # type: ignore
            raise PermissionDenied("You do not have permission to perform this action.")

    def retrieve(self, request, *args, **kwargs):
        post = get_object_or_404(PostModel, pk=kwargs.get("pk"))
        self.check_post_permissions(post)
        serializer = self.get_serializer(post)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        post = get_object_or_404(PostModel, pk=kwargs.get("pk"))
        self.check_post_permissions(post)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        post = get_object_or_404(PostModel, pk=kwargs.get("pk"))
        self.check_post_permissions(post)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["POST"], detail=False, url_path="like")
    def like_post(self, request, *args, **kwargs):
        post_id = request.data.get("post_id")

        if not post_id:
            raise ValidationError({"detail": "Post ID(post_id) is required."})

        post = get_object_or_404(PostModel, pk=post_id)

        if post.liked_by.filter(pk=request.user.pk).exists():
            raise ValidationError({"detail": "You already liked this post."})

        post.liked_by.add(request.user)
        post.likes_counter += 1
        post.save()

        return Response(status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path="dislike")
    def dislike_post(self, request, *args, **kwargs):
        post_id = request.data.get("post_id")

        if not post_id:
            raise ValidationError({"detail": "Post ID(post_id) is required."})

        post = get_object_or_404(PostModel, pk=post_id)

        if post.liked_by.filter(pk=request.user.pk).exists():
            post.liked_by.remove(request.user)
            post.likes_counter -= 1
            post.save()
            return Response(status=status.HTTP_200_OK)

        raise ValidationError(
            {"detail": "You can not dislike a post you have not liked yet."}
        )
