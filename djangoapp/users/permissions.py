from rest_framework.permissions import BasePermission
from rest_framework.validators import ValidationError


class CanCreate(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated is False or request.user.is_staff is True:
            return True
        raise ValidationError(
            {
                "Error detail": "You are already logged in and cannot create a new account."
            }
        )
