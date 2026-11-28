from rest_framework import serializers
from drf_spectacular.utils import OpenApiTypes, extend_schema_field

from .models import Category, Reply, Ticket, TicketEvent


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = fields


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
        fields = ['id', 'title', 'status', 'priority', 'category', 'created_by', 'assignee', 'created_at', 'updated_at']
        read_only_fields = fields

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_created_by(self, obj):
        return {'id': obj.created_by_id, 'username': obj.created_by.username}

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_assignee(self, obj):
        return {'id': obj.assignee_id, 'username': obj.assignee.username} if obj.assignee else None


class TicketDetailSerializer(TicketListSerializer):
    replies = ReplySerializer(many=True, read_only=True)
    events = TicketEventSerializer(many=True, read_only=True)

    class Meta(TicketListSerializer.Meta):
        fields = TicketListSerializer.Meta.fields + ['description', 'replies', 'events']


class TicketCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=160, trim_whitespace=True)
    description = serializers.CharField(max_length=10000, trim_whitespace=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.filter(is_active=True))
    priority = serializers.ChoiceField(choices=Ticket.Priority.choices, default=Ticket.Priority.NORMAL)

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
