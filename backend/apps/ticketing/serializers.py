from rest_framework import serializers
from drf_spectacular.utils import OpenApiTypes, extend_schema_field

from .models import Category, Reply, Ticket, TicketEvent


class CategorySerializer(serializers.ModelSerializer):
    form = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'department', 'parent', 'form']
        read_only_fields = fields

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_form(self, obj):
        return {'id': obj.form_id, 'version': obj.form.version, 'fields': obj.form.fields} if obj.form_id else None


class ReplySerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = ['id', 'author', 'body', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_author(self, obj):
        return {'id': obj.author_id, 'username': obj.author.username, 'role': obj.author.role}


class TicketEventSerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()

    class Meta:
        model = TicketEvent
        fields = ['id', 'action', 'detail', 'actor', 'created_at']
        read_only_fields = fields

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_actor(self, obj):
        return {'id': obj.actor_id, 'username': obj.actor.username} if obj.actor else None


class TicketListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    assignee = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id', 'tracking_number', 'title', 'status', 'priority', 'category', 'department', 'confidentiality', 'created_by', 'assignee', 'created_at', 'updated_at', 'response_due_at', 'resolution_due_at', 'first_response_at', 'resolved_at', 'version']
        read_only_fields = fields

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_created_by(self, obj):
        return {'id': obj.created_by_id, 'username': obj.created_by.username}

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_assignee(self, obj):
        return {'id': obj.assignee_id, 'username': obj.assignee.username} if obj.assignee else None


class TicketDetailSerializer(TicketListSerializer):
    replies = ReplySerializer(many=True, read_only=True)
    events = serializers.SerializerMethodField()
    internal_notes = serializers.SerializerMethodField()
    allowed_actions = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_allowed_actions(self, obj):
        from apps.portal.permissions import has_permission
        from .services import TRANSITIONS
        user = self.context['request'].user
        permissions = ['reply', 'assign', 'transfer', 'resolve', 'close', 'reopen', 'add_internal_note', 'change_priority']
        return {'permissions': [p for p in permissions if has_permission(user, 'ticket.' + p, obj.department_id)], 'transitions': sorted(TRANSITIONS.get(obj.status, []))}

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_events(self, obj):
        events = obj.events.all()
        if self.context['request'].user.role == 'student':
            events = events.filter(is_internal=False)
        return TicketEventSerializer(events, many=True).data

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_internal_notes(self, obj):
        from apps.portal.permissions import has_permission
        user = self.context['request'].user
        if user.role == 'student' or not has_permission(user, 'ticket.add_internal_note', obj.department_id):
            return []
        return list(obj.internal_notes.values('id', 'body', 'author__username', 'created_at'))

    class Meta(TicketListSerializer.Meta):
        fields = TicketListSerializer.Meta.fields + ['description', 'replies', 'events', 'internal_notes', 'allowed_actions', 'form_snapshot', 'form_responses', 'resolution_summary']


class TicketCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=160, trim_whitespace=True)
    description = serializers.CharField(max_length=10000, trim_whitespace=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.filter(is_active=True))
    priority = serializers.ChoiceField(choices=Ticket.Priority.choices, default=Ticket.Priority.NORMAL)
    form_responses = serializers.JSONField(default=dict)

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError('Title cannot be blank.')
        return value

    def validate_description(self, value):
        if not value.strip():
            raise serializers.ValidationError('Description cannot be blank.')
        return value


class ReplyCreateSerializer(serializers.Serializer):
    body = serializers.CharField(max_length=10000, trim_whitespace=True)

    def validate_body(self, value):
        if not value.strip():
            raise serializers.ValidationError('Reply cannot be blank.')
        return value


class StatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Ticket.Status.choices)
    reason = serializers.CharField(max_length=2000, required=False, allow_blank=True, default='')
