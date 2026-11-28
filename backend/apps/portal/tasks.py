from datetime import timedelta

from celery import shared_task
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from apps.ticketing.models import Ticket, TicketEvent
from apps.ticketing.services import _notify, visible_tickets
from .models import Escalation, Notification, SiteSettings


@shared_task(ignore_result=True)
def monitor_service_levels():
    now = timezone.now()
    cache.set('worker:heartbeat', now.isoformat(), 180)
    ids = Ticket.objects.exclude(status__in=['closed', 'resolved']).values_list('pk', flat=True)
    for pk in ids.iterator(chunk_size=100):
        with transaction.atomic():
            ticket = Ticket.objects.select_for_update().select_related('category__sla_policy', 'department').get(pk=pk)
            if ticket.status in ('resolved', 'closed') or not ticket.category.sla_policy_id:
                continue
            policy = ticket.category.sla_policy
            for kind, deadline in [('response', ticket.response_due_at), ('resolution', ticket.resolution_due_at)]:
                if deadline is None or kind == 'response' and ticket.first_response_at or kind == 'resolution' and ticket.sla_paused_at:
                    continue
                if deadline > now + timedelta(minutes=policy.warning_minutes):
                    continue
                trigger = kind + ('_breach' if deadline <= now else '_warning')
                escalation, created = Escalation.objects.get_or_create(ticket=ticket, trigger=trigger, level=1, defaults={'reason': 'پایش خودکار زمان پاسخگویی'})
                if not created:
                    continue
                TicketEvent.objects.create(ticket=ticket, action='status_changed', detail='هشدار زمان پاسخگویی', is_internal=True)
                if ticket.department_id:
                    for member in ticket.department.memberships.filter(is_manager=True).select_related('user'):
                        if visible_tickets(member.user).filter(pk=ticket.pk).exists():
                            Notification.objects.get_or_create(idempotency_key=f'escalation:{escalation.pk}:user:{member.user_id}', defaults={'user': member.user, 'ticket': ticket, 'title': 'هشدار زمان پاسخگویی', 'category': 'sla'})
    settings, _ = SiteSettings.objects.get_or_create(pk=1)
    for pk in Ticket.objects.filter(status='resolved', resolved_at__lte=now - timedelta(days=settings.auto_close_days)).values_list('pk', flat=True).iterator():
        with transaction.atomic():
            ticket = Ticket.objects.select_for_update().get(pk=pk)
            if ticket.status != 'resolved':
                continue
            ticket.status = 'closed'
            ticket.version += 1
            ticket.save()
            TicketEvent.objects.create(ticket=ticket, action='closed', detail='بسته شدن خودکار پس از مهلت تأیید')
            _notify(ticket, 'درخواست پس از پایان مهلت تأیید بسته شد')
