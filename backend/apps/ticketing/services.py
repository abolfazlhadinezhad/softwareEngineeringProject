from django.db import transaction
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError

from .models import Category, Reply, Ticket, TicketEvent


class TicketConflict(APIException):
    status_code = 409
    default_detail = 'The ticket changed before this action completed.'
    default_code = 'conflict'


def visible_tickets(user):
    queryset = Ticket.objects.select_related('created_by', 'category', 'assignee')
    if user.role == 'student':
        queryset = queryset.filter(created_by=user)
    return queryset


def _record(ticket, actor, action, detail=''):
    TicketEvent.objects.create(ticket=ticket, actor=actor, action=action, detail=detail[:255])


def create_ticket(*, actor, title, description, category, priority):
    with transaction.atomic():
        ticket = Ticket.objects.create(created_by=actor, title=title.strip(), description=description.strip(), category=category, priority=priority)
        _record(ticket, actor, TicketEvent.Action.CREATED, 'Ticket submitted')
    return ticket


def add_reply(*, ticket, actor, body):
    with transaction.atomic():
        locked = Ticket.objects.select_for_update().get(pk=ticket.pk)
        if locked.status == Ticket.Status.CLOSED:
            raise ValidationError({'detail': 'Closed tickets must be reopened before replying.'})
        reply = Reply.objects.create(ticket=locked, author=actor, body=body.strip())
        locked.save(update_fields=['updated_at'])
        _record(locked, actor, TicketEvent.Action.REPLIED, 'Reply added')
    return reply


def claim_ticket(*, ticket, actor):
    if actor.role not in ('support', 'admin'):
        raise PermissionDenied('Only support staff can claim tickets.')
    with transaction.atomic():
        locked = Ticket.objects.select_for_update().get(pk=ticket.pk)
        if locked.assignee_id and locked.assignee_id != actor.pk:
            raise TicketConflict('This ticket is already assigned to another support user.')
        if locked.status == Ticket.Status.CLOSED:
            raise ValidationError({'detail': 'Closed tickets cannot be claimed.'})
        locked.assignee = actor
        locked.status = Ticket.Status.IN_PROGRESS
        locked.save(update_fields=['assignee', 'status', 'updated_at'])
        _record(locked, actor, TicketEvent.Action.CLAIMED, f'Claimed by {actor.username}')
    return locked


def release_ticket(*, ticket, actor):
    if actor.role not in ('support', 'admin'):
        raise PermissionDenied('Only support staff can release tickets.')
    with transaction.atomic():
        locked = Ticket.objects.select_for_update().get(pk=ticket.pk)
        if locked.assignee_id and locked.assignee_id != actor.pk and actor.role != 'admin':
            raise PermissionDenied('Only the assignee or an administrator can release this ticket.')
        locked.assignee = None
        if locked.status == Ticket.Status.IN_PROGRESS:
            locked.status = Ticket.Status.OPEN
        locked.save(update_fields=['assignee', 'status', 'updated_at'])
        _record(locked, actor, TicketEvent.Action.RELEASED, 'Assignment released')
    return locked


def change_status(*, ticket, actor, status):
    if actor.role not in ('support', 'admin'):
        raise PermissionDenied('Only support staff can change ticket status.')
    if status not in Ticket.Status.values:
        raise ValidationError({'status': 'Choose a valid ticket status.'})
    with transaction.atomic():
        locked = Ticket.objects.select_for_update().get(pk=ticket.pk)
        if locked.status == Ticket.Status.CLOSED and status != Ticket.Status.OPEN:
            raise ValidationError({'status': 'Closed tickets can only be reopened to open.'})
        old = locked.status
        locked.status = status
        locked.save(update_fields=['status', 'updated_at'])
        action = TicketEvent.Action.CLOSED if status == Ticket.Status.CLOSED else TicketEvent.Action.REOPENED if old == Ticket.Status.CLOSED else TicketEvent.Action.STATUS_CHANGED
        _record(locked, actor, action, f'{old} -> {status}')
    return locked


def student_close(*, ticket, actor):
    with transaction.atomic():
        locked = Ticket.objects.select_for_update().get(pk=ticket.pk)
        if locked.created_by_id != actor.pk:
            raise PermissionDenied('Only the ticket creator can close this ticket.')
        if locked.status == Ticket.Status.CLOSED:
            return locked
        old = locked.status
        locked.status = Ticket.Status.CLOSED
        locked.save(update_fields=['status', 'updated_at'])
        _record(locked, actor, TicketEvent.Action.CLOSED, f'{old} -> closed')
    return locked


def student_reopen(*, ticket, actor):
    with transaction.atomic():
        locked = Ticket.objects.select_for_update().get(pk=ticket.pk)
        if locked.created_by_id != actor.pk:
            raise PermissionDenied('Only the ticket creator can reopen this ticket.')
        if locked.status != Ticket.Status.CLOSED:
            raise ValidationError({'status': 'Only closed tickets can be reopened.'})
        locked.status = Ticket.Status.OPEN
        locked.save(update_fields=['status', 'updated_at'])
        _record(locked, actor, TicketEvent.Action.REOPENED, 'Ticket reopened by creator')
    return locked
