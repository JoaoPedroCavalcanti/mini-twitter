from rest_framework.routers import SimpleRouter

from users.views import UserViewSet

app_name = "users"

user_routers = SimpleRouter()
user_routers.register("", UserViewSet, basename="users-api")
urlpatterns = user_routers.urls
