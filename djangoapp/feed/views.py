from posts.models import PostModel
from posts.serializers import PostSerializer
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class FeedView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        following_users = user.profile.following.all().values_list("user", flat=True)  # type: ignore

        return PostModel.objects.filter(poster_user__in=following_users).order_by(
            "-created_at"
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response(
            {"detail": "No posts found from users you are following."},
            status=status.HTTP_200_OK,
        )