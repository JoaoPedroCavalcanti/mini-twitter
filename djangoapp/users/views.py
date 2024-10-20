from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from users.permissions import CanCreate
from users.serializers import UserSerializer


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'delete', 'patch']
    permission_classes = [IsAuthenticated, ]
    
    def get_queryset(self):
        User = get_user_model()
        
        if self.request.user.is_staff: # type: ignore
            return User.objects.all()
        
        return User.objects.filter(pk=self.request.user.pk)
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [CanCreate()]
        return super().get_permissions()