from datetime import timedelta

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError

from apps.portal.models import AccessGrant, Notification, Profile, SiteSettings
from apps.portal.permissions import audit, department_ids, has_permission, require
from .models import InternalNote, Reply, Ticket, TicketEvent


class TicketConflict(APIException):
    status_code = 409
    default_detail = 'درخواست هم‌زمان تغییر کرده است. اطلاعات را تازه کنید.'
    default_code = 'conflict'


TRANSITIONS = {
    'open': {'in_progress'},
    'in_progress': {'open', 'waiting_student', 'resolved'},
    'waiting_student': {'in_progress', 'resolved'},
    'resolved': {'closed', 'open'},
    'closed': {'open'},
}


def visible_tickets(user):
    qs = Ticket.objects.select_related('created_by', 'category', 'assignee', 'department')
    if not user.is_authenticated or not user.is_active:
        return qs.none()
    if user.role == 'student':
        return qs.filter(created_by=user)
    grants = AccessGrant.objects.filter(user=user, expires_at__gt=timezone.now()).values('ticket_id')
    scope = Q(department_id__in=department_ids(user))
    if has_permission(user, 'ticket.view.assigned'):
        scope |= Q(assignee=user)
    else:
        scope |= Q(assignee=user, department_id__in=department_ids(user, 'ticket.view.assigned'))
    if has_permission(user, 'ticket.view.all'):
        scope = Q()
    sensitive = Q(confidentiality='normal') | Q(pk__in=grants)
    if has_permission(user, 'ticket.view.confidential'):
        sensitive = Q()
    else:
        sensitive |= Q(department_id__in=department_ids(user, 'ticket.view.confidential'))
    return qs.filter((scope & sensitive) | Q(pk__in=grants)).distinct()


def _record(ticket, actor, action, detail='', internal=False):
    TicketEvent.objects.create(ticket=ticket, actor=actor, action=action, detail=detail[:255], is_internal=internal)


def _notify(ticket, title, *, internal=False):
    recipients = [] if internal else [ticket.created_by_id]
    if ticket.assignee_id and visible_tickets(ticket.assignee).filter(pk=ticket.pk).exists():
        recipients.append(ticket.assignee_id)
    disabled = set(Profile.objects.filter(user_id__in=recipients, notification_preferences__in_app=False).values_list('user_id', flat=True))
    Notification.objects.bulk_create([Notification(user_id=pk, ticket=ticket, title=title) for pk in set(recipients) - disabled])


def _lock(ticket, actor, permission):
    locked = Ticket.objects.select_for_update().select_related('department', 'category__sla_policy').get(pk=ticket.pk)
    if not visible_tickets(actor).filter(pk=locked.pk).exists():
        raise PermissionDenied('دسترسی به درخواست مجاز نیست.')
    require(actor, permission, locked.department_id)
    return locked


@transaction.atomic
def create_ticket(*, actor, title, description, category, priority='normal', form_responses=None):
    require(actor, 'ticket.create')
    if actor.role != 'student':
        raise PermissionDenied('ثبت درخواست برای دانشجویان است.')
    if category.department_id is None or not category.is_active or not category.department.is_active or not category.department.is_public:
        raise ValidationError({'category': 'واحد فعال برای این دسته‌بندی تنظیم نشده است.'})
    from apps.portal.forms import validate_submission
    snapshot, responses = validate_submission(category.form, form_responses or {})
    ticket = Ticket.objects.create(
        created_by=actor, title=title.strip(), description=description.strip(), category=category,
        department=category.department, priority=category.default_priority,
        confidentiality=category.department.confidentiality, form_snapshot=snapshot, form_responses=responses,
    )
    if category.sla_policy_id:
        from apps.portal.sla import add_business_minutes
        ticket.response_due_at = add_business_minutes(ticket.created_at, category.sla_policy.first_response_minutes, category.sla_policy.calendar)
        ticket.resolution_due_at = add_business_minutes(ticket.created_at, category.sla_policy.resolution_minutes, category.sla_policy.calendar)
        ticket.save()
    _record(ticket, actor, TicketEvent.Action.CREATED, 'درخواست ثبت شد')
    _notify(ticket, 'درخواست شما دریافت شد')
    return ticket


@transaction.atomic
def add_reply(*, ticket, actor, body):
    locked = _lock(ticket, actor, 'ticket.reply')
    if locked.status in ('closed', 'resolved'):
        raise ValidationError({'detail': 'ابتدا درخواست را بازگشایی کنید.'})
    reply = Reply.objects.create(ticket=locked, author=actor, body=body.strip())
    if actor.role != 'student' and not locked.first_response_at:
        locked.first_response_at = timezone.now()
    if actor.role == 'student' and locked.status == 'waiting_student':
        _transition(locked, actor, 'in_progress', 'پاسخ دانشجو دریافت شد')
    locked.version += 1
    locked.save()
    _record(locked, actor, TicketEvent.Action.REPLIED, 'پاسخ جدید')
    _notify(locked, 'پاسخ جدید برای درخواست ثبت شد')
    return reply


@transaction.atomic
def claim_ticket(*, ticket, actor):
    if actor.role == 'student':
        raise PermissionDenied('این عملیات برای کارکنان است.')
    locked = _lock(ticket, actor, 'ticket.assign')
    if locked.assignee_id and locked.assignee_id != actor.pk:
        raise TicketConflict('درخواست قبلاً به کارشناس دیگری واگذار شده است.')
    if locked.status != 'open':
        raise ValidationError({'detail': 'فقط درخواست باز قابل دریافت است.'})
    locked.assignee = actor
    _transition(locked, actor, 'in_progress', 'کارشناس مسئول مشخص شد')
    _record(locked, actor, TicketEvent.Action.CLAIMED, 'مسئول رسیدگی مشخص شد')
    return locked


@transaction.atomic
def release_ticket(*, ticket, actor, reason=''):
    locked = _lock(ticket, actor, 'ticket.assign')
    if not reason.strip():
        raise ValidationError({'reason': 'دلیل تغییر مسئول الزامی است.'})
    if locked.assignee_id != actor.pk and not has_permission(actor, 'ticket.transfer', locked.department_id):
        raise PermissionDenied('مجوز تغییر مسئول ندارید.')
    if locked.status not in ('open', 'in_progress'):
        raise ValidationError({'detail': 'ابتدا درخواست را به وضعیت در حال بررسی برگردانید.'})
    locked.assignee = None
    if locked.status == 'in_progress':
        _transition(locked, actor, 'open', reason)
    else:
        locked.save()
    _record(locked, actor, TicketEvent.Action.RELEASED, 'درخواست به صف رسیدگی بازگشت')
    audit(actor, 'ticket.release', locked.pk, locked.department, reason=reason)
    return locked


def _transition(ticket, actor, status, reason=''):
    if status not in TRANSITIONS.get(ticket.status, set()):
        raise ValidationError({'status': 'این تغییر وضعیت مجاز نیست.'})
    old = ticket.status
    now = timezone.now()
    if old == 'waiting_student' and ticket.sla_paused_at:
        from apps.portal.sla import add_business_minutes, business_minutes_between
        policy = ticket.category.sla_policy
        if policy and ticket.resolution_due_at:
            paused = business_minutes_between(ticket.sla_paused_at, now, policy.calendar)
            ticket.resolution_due_at = add_business_minutes(ticket.resolution_due_at, paused, policy.calendar)
        ticket.sla_paused_at = None
    if status == 'waiting_student' and ticket.category.sla_policy_id and ticket.category.sla_policy.pause_waiting_student:
        ticket.sla_paused_at = now
    if status == 'resolved':
        ticket.resolved_at = now
        ticket.resolution_summary = reason
    ticket.status = status
    ticket.version += 1
    ticket.save()
    _record(ticket, actor, TicketEvent.Action.STATUS_CHANGED, f'{old} → {status}')
    _notify(ticket, 'وضعیت درخواست تغییر کرد')


@transaction.atomic
def change_status(*, ticket, actor, status, reason=''):
    if actor.role == 'student':
        raise PermissionDenied('مجوز تغییر وضعیت ندارید.')
    permission = 'ticket.resolve' if status == 'resolved' else 'ticket.close' if status == 'closed' else 'ticket.reopen' if status == 'open' else 'ticket.reply'
    locked = _lock(ticket, actor, permission)
    if status in ('resolved', 'closed', 'open') and not reason.strip():
        raise ValidationError({'reason': 'دلیل یا شرح نتیجه رسیدگی الزامی است.'})
    _transition(locked, actor, status, reason)
    audit(actor, 'ticket.transition', locked.pk, locked.department, status=status, reason=reason)
    return locked


@transaction.atomic
def student_close(*, ticket, actor):
    locked = _lock(ticket, actor, 'ticket.close')
    if actor.pk != locked.created_by_id or locked.status != 'resolved':
        raise ValidationError({'detail': 'تأیید حل مسئله فقط پس از ارائه نتیجه امکان‌پذیر است.'})
    _transition(locked, actor, 'closed', 'حل مسئله توسط دانشجو تأیید شد')
    return locked


@transaction.atomic
def student_reopen(*, ticket, actor, reason=''):
    locked = _lock(ticket, actor, 'ticket.reopen')
    policy, _ = SiteSettings.objects.get_or_create(pk=1)
    if actor.pk != locked.created_by_id or locked.status not in ('resolved', 'closed'):
        raise ValidationError({'detail': 'درخواست قابل بازگشایی نیست.'})
    if not locked.resolved_at or timezone.now() > locked.resolved_at + timedelta(days=policy.reopen_days):
        raise ValidationError({'detail': 'مهلت بازگشایی پایان یافته است.'})
    if not reason.strip():
        raise ValidationError({'reason': 'دلیل بازگشایی را وارد کنید.'})
    _transition(locked, actor, 'open', reason)
    _record(locked, actor, TicketEvent.Action.REOPENED, reason)
    return locked


@transaction.atomic
def add_note(*, ticket, actor, body):
    locked = _lock(ticket, actor, 'ticket.add_internal_note')
    note = InternalNote.objects.create(ticket=locked, author=actor, body=body.strip())
    _record(locked, actor, TicketEvent.Action.REPLIED, 'یادداشت داخلی ثبت شد', internal=True)
    _notify(locked, 'یادداشت داخلی جدید', internal=True)
    return note


@transaction.atomic
def transfer_ticket(*, ticket, actor, department, category, reason):
    locked = _lock(ticket, actor, 'ticket.transfer')
    if not reason.strip() or not department.is_active or category.department_id != department.pk or not category.is_active:
        raise ValidationError({'detail': 'واحد، دسته‌بندی فعال و دلیل انتقال را مشخص کنید.'})
    if locked.status in ('closed', 'resolved'):
        raise ValidationError({'detail': 'ابتدا درخواست را بازگشایی کنید.'})
    if locked.confidentiality != 'normal' and department.confidentiality == 'normal':
        raise ValidationError({'detail': 'انتقال درخواست حساس به صف عادی مجاز نیست.'})
    previous = locked.department
    locked.department = department
    locked.category = category
    locked.assignee = None
    if department.confidentiality != 'normal':
        locked.confidentiality = department.confidentiality
    locked.version += 1
    locked.save()
    _record(locked, actor, TicketEvent.Action.STATUS_CHANGED, 'درخواست به واحد مسئول جدید منتقل شد')
    audit(actor, 'ticket.transfer', locked.pk, department, previous_department=previous.pk if previous else None, reason=reason)
    _notify(locked, 'واحد رسیدگی به درخواست تغییر کرد')
    return locked

