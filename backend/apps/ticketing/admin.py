from django.contrib import admin
from .models import Category, Reply, Ticket, TicketEvent
from .services import visible_tickets
from apps.portal.permissions import audit


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


class ReplyInline(admin.TabularInline):
    model = Reply
    extra = 0
    readonly_fields = ('author', 'body', 'created_at')

    def has_add_permission(self, request, obj=None): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_by', 'category', 'status', 'priority', 'assignee', 'updated_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description', 'created_by__username')
    readonly_fields = tuple(field.name for field in Ticket._meta.fields)
    inlines = [ReplyInline]

    def get_queryset(self, request):
        return visible_tickets(request.user)

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        if obj and obj.confidentiality != 'normal':
            audit(request.user, 'ticket.confidential_maintenance_access', obj.pk, obj.department)
        return obj

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(TicketEvent)
class TicketEventAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'action', 'actor', 'created_at')
    list_filter = ('action',)
    readonly_fields = ('ticket', 'actor', 'action', 'detail', 'is_internal', 'created_at')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(ticket__in=visible_tickets(request.user))

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
