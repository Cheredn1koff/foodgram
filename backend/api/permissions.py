from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsNotBannedPermission(BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            and view.name not in ['Download shopping cart', 'Subscriptions']
            or request.user.is_active and request.user.is_authenticated
        )


class IsAuthorAdminOrReadOnlyPermission(IsNotBannedPermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user == obj.author
            or request.user.is_staff
        )
