from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.viewsets import ModelViewSet

from users.permissions import CanCreate
from users.serializers import UserSerializer


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    http_method_names = ["get", "post", "delete", "patch"]
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        User = get_user_model()

        if self.request.user.is_staff or self.request.method == "GET":  # type: ignore
            return User.objects.all()

        return User.objects.filter(pk=self.request.user.pk)

    def get_permissions(self):
        if self.request.method == "POST" and not (
            "follow/" in self.request.path or "unfollow" in self.request.path
        ):
            return [CanCreate()]
        return super().get_permissions()

    @action(
        methods=["POST"],
        detail=False,
        url_path="follow",
        permission_classes=[IsAuthenticated],
    )
    def follow(self, request, *args, **kwargs):
        User = get_user_model()

        user_following = request.user

        id_user_to_follow = request.data.get("id_user_to_follow")

        if not id_user_to_follow:
            raise ValidationError({"error": "User ID(id_user_to_follow) is required."})

        user_to_follow = get_object_or_404(User, id=id_user_to_follow)

        # User can not follow who his already follow
        if user_following.profile.following.filter(
            pk=user_to_follow.profile.pk  # type: ignore
        ).exists():
            raise ValidationError({"detail": "You are already following this user."})

        # User can not follow itself
        if user_following == user_to_follow:
            raise ValidationError({"detail": "You can not follow yourself."})

        # User can not follow an admin user
        if user_to_follow.is_staff:
            raise ValidationError({"detail": "You can not follow this user."})

        user_following.profile.following.add(user_to_follow.profile)  # type: ignore
        user_to_follow.profile.followers.add(user_following.profile)  # type: ignore
        return Response(
            {"detail": "Successfully followed the user."},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        methods=["POST"],
        detail=False,
        url_path="unfollow",
    )
    def unfollow(self, request, *args, **kwargs):
        User = get_user_model()

        user_unfollowing = request.user

        id_user_to_unfollow = request.data.get("id_user_to_unfollow")
        if not id_user_to_unfollow:
            raise ValidationError(
                {"error": "User ID(id_user_to_unfollow) is required."}
            )

        user_to_unfollow = get_object_or_404(User, id=id_user_to_unfollow)

        if user_unfollowing.profile.following.filter(
            pk=user_to_unfollow.profile.pk  # type: ignore
        ).exists():
            user_unfollowing.profile.following.remove(user_to_unfollow.profile)  # type: ignore
            user_to_unfollow.profile.followers.remove(user_unfollowing.profile)  # type: ignore
            return Response(
                {"detail": "Successfully unfollowed the user."},
                status=status.HTTP_204_NO_CONTENT,
            )
        raise ValidationError({"detail": "You are not following this user."})
