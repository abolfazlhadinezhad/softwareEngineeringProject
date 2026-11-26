from django.contrib import admin
from .models import Category, Reply, Ticket, TicketEvent


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


class ReplyInline(admin.TabularInline):
    model = Reply
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_by', 'category', 'status', 'priority', 'assignee', 'updated_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ReplyInline]


@admin.register(TicketEvent)
class TicketEventAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'action', 'actor', 'created_at')
    list_filter = ('action',)
    readonly_fields = ('ticket', 'actor', 'action', 'detail', 'created_at')
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
