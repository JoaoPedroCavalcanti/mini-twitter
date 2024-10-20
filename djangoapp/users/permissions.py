from rest_framework.permissions import BasePermission

class CanCreate(BasePermission):
    
    def has_permission(self, request, view):
        if request.user.is_authenticated == False and request.user.is_staff == True:
            return True
        return False