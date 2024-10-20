from django.urls import path
from rest_framework.routers import SimpleRouter
from users.views import UserViewSet

user_routers = SimpleRouter()
user_routers.register(
    '',
    UserViewSet,
    basename='users-api'
)
print(user_routers.urls)
urlpatterns = user_routers.urls
