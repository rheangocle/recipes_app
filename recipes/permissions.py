from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Only allow ownders of an object to edit it"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        return False
    
class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """Allow read access to all users, write acces to authenticated users only"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated