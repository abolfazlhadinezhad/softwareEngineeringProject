import uuid

from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    department = models.ForeignKey('portal.Department', on_delete=models.PROTECT, null=True, blank=True, related_name='categories')
    parent = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True)
    form = models.ForeignKey('portal.RequestForm', on_delete=models.PROTECT, null=True, blank=True)
    sla_policy = models.ForeignKey('portal.SLAPolicy', on_delete=models.PROTECT, null=True, blank=True)
    default_priority = models.CharField(max_length=10, default='normal', choices=[('low', 'Low'), ('normal', 'Normal'), ('high', 'High')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In progress'
        WAITING_STUDENT = 'waiting_student', 'Waiting for student'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        NORMAL = 'normal', 'Normal'
        HIGH = 'high', 'High'

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_tickets')
    tracking_number = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    department = models.ForeignKey('portal.Department', on_delete=models.PROTECT, null=True, blank=True, related_name='tickets')
    confidentiality = models.CharField(max_length=20, default='normal', choices=[('normal', 'Normal'), ('restricted', 'Restricted'), ('confidential', 'Confidential')])
    form_snapshot = models.JSONField(default=dict)
    form_responses = models.JSONField(default=dict)
    first_response_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    response_due_at = models.DateTimeField(null=True, blank=True, db_index=True)
    resolution_due_at = models.DateTimeField(null=True, blank=True, db_index=True)
    sla_paused_at = models.DateTimeField(null=True, blank=True)
    resolution_summary = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=1)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='tickets')
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    title = models.CharField(max_length=160)
    description = models.TextField(max_length=10000)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at', '-id')
        indexes = [
            models.Index(fields=('created_by', '-updated_at'), name='ticket_creator_updated_idx'),
            models.Index(fields=('status', '-updated_at'), name='ticket_status_updated_idx'),
            models.Index(fields=('category', '-updated_at'), name='ticket_category_updated_idx'),
            models.Index(fields=('department', 'status', '-updated_at'), name='ticket_department_status_idx'),
            models.Index(fields=('assignee', 'status'), name='ticket_assignee_status_idx'),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(status__in=['open', 'in_progress', 'waiting_student', 'resolved', 'closed']), name='valid_ticket_status'),
            models.CheckConstraint(condition=models.Q(priority__in=['low', 'normal', 'high']), name='valid_ticket_priority'),
        ]

    def __str__(self):
        return f'#{self.pk} {self.title}'


class Reply(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ticket_replies')
    body = models.TextField(max_length=10000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at', 'id')


class TicketEvent(models.Model):
    class Action(models.TextChoices):
        CREATED = 'created', 'Created'
        REPLIED = 'replied', 'Replied'
        CLAIMED = 'claimed', 'Claimed'
        RELEASED = 'released', 'Released'
        STATUS_CHANGED = 'status_changed', 'Status changed'
        CLOSED = 'closed', 'Closed'
        REOPENED = 'reopened', 'Reopened'

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='events')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='ticket_events')
    action = models.CharField(max_length=20, choices=Action.choices)
    detail = models.CharField(max_length=255, blank=True)
    is_internal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at', '-id')


class InternalNote(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='internal_notes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    body = models.TextField(max_length=10000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']
