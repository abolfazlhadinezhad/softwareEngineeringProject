from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class AccountAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Profile', {'fields': ('first_name', 'last_name', 'email')}),
        ('Access', {'fields': ('role', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (('Role', {'fields': ('role',)}),)

    def has_module_permission(self, request):
        return request.user.is_authenticated and request.user.role == User.Role.ADMIN

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated and request.user.role == User.Role.ADMIN

    has_add_permission = has_view_permission
    has_change_permission = has_view_permission
    has_delete_permission = has_view_permission
