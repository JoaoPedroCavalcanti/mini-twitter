from rest_framework.routers import SimpleRouter

from posts.views import PostViewSet

post_router = SimpleRouter()
post_router.register('', PostViewSet, basename='post')

urlpatterns = post_router.urls
