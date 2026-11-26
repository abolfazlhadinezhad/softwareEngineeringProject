from rest_framework.permissions import BasePermission


def is_staff_role(user):
    return user.is_authenticated and user.role in ('support', 'admin')


class IsSupportOrAdmin(BasePermission):
    message = 'Support staff access is required for this action.'

    def has_permission(self, request, view):
        return is_staff_role(request.user)
