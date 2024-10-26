from rest_framework.routers import SimpleRouter

from posts.views import PostViewSet

app_name = "posts"


post_router = SimpleRouter()
post_router.register("", PostViewSet, basename="posts-api")

urlpatterns = post_router.urls
