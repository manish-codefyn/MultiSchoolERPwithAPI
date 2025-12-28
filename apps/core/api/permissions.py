from rest_framework import permissions
from django.core.exceptions import PermissionDenied

class TenantAccessPermission(permissions.BasePermission):
    """
    Ensure user can only access their tenant's data
    """
    def has_object_permission(self, request, view, obj):
        # Superuser bypass
        if request.user.is_superuser:
            return True

        if not hasattr(request.user, 'tenant'):
            return False

        # Check if object belongs to user's tenant
        if hasattr(obj, 'tenant'):
            return obj.tenant == request.user.tenant
            
        return True

class RoleRequiredPermission(permissions.BasePermission):
    """
    Check if user has required role(s) defined in the view
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True

        required_roles = getattr(view, 'required_roles', None)
        min_role_level = getattr(view, 'min_role_level', None)
        
        # If no role restrictions, allow
        if not required_roles and not min_role_level:
            return True
            
        # Check specific roles
        if required_roles:
            if isinstance(required_roles, str):
                if request.user.role == required_roles:
                    return True
            elif request.user.role in required_roles:
                return True
                
        # Check role level validation (if applicable)
        if min_role_level:
            from apps.users.models import ROLE_HIERARCHY
            user_level = ROLE_HIERARCHY.get(request.user.role, 0)
            if user_level >= min_role_level:
                return True
                
        return False

class HasModelPermission(permissions.DjangoModelPermissions):
    """
    Extended DjangoModelPermissions to work with custom Permission Logic if needed
    """
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }
