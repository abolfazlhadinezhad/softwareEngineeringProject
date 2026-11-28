from statistics import mean, median

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiTypes, extend_schema

from apps.ticketing.models import Ticket
from apps.ticketing.serializers import TicketListSerializer
from apps.ticketing.services import visible_tickets
from .models import Department, Feedback, Membership
from .permissions import department_ids, has_permission


@extend_schema(responses=OpenApiTypes.OBJECT)
class DashboardView(APIView):
    def get(self, request):
        user = request.user
        tickets = visible_tickets(user)
        counts = dict(tickets.values_list('status').annotate(count=Count('pk')))
        result = {'counts': counts, 'total': sum(counts.values()), 'unassigned': tickets.filter(assignee__isnull=True).exclude(status__in=['closed', 'resolved']).count(), 'overdue': tickets.filter(resolution_due_at__lt=timezone.now(), sla_paused_at__isnull=True).exclude(status__in=['closed', 'resolved']).count(), 'recent': TicketListSerializer(tickets[:5], many=True).data}
        if user.role != 'student':
            result['my_queue'] = TicketListSerializer(tickets.filter(assignee=user).exclude(status__in=['closed', 'resolved'])[:5], many=True).data
        ids = department_ids(user, 'report.view.department')
        if ids or has_permission(user, 'report.view.university'):
            reporting = Ticket.objects.all() if has_permission(user, 'report.view.university') else Ticket.objects.filter(department_id__in=ids)
            result['by_department'] = list(reporting.values('department__name').annotate(count=Count('pk')).order_by('-count'))
            result['workload'] = list(reporting.exclude(status__in=['closed', 'resolved']).values('assignee__username').annotate(count=Count('pk')).order_by('-count'))
            first = [(row.first_response_at - row.created_at).total_seconds() / 60 for row in reporting.filter(first_response_at__isnull=False).only('created_at', 'first_response_at').iterator()]
            resolved = [(row.resolved_at - row.created_at).total_seconds() / 60 for row in reporting.filter(resolved_at__isnull=False).only('created_at', 'resolved_at').iterator()]
            result['performance'] = {'first_response_mean_minutes': mean(first) if first else None, 'first_response_median_minutes': median(first) if first else None, 'resolution_mean_minutes': mean(resolved) if resolved else None, 'resolution_median_minutes': median(resolved) if resolved else None, 'responded_count': len(first), 'resolved_count': len(resolved)}
            result['satisfaction'] = Feedback.objects.filter(ticket__in=reporting).aggregate(average=Avg('overall'), responses=Count('pk'))
            result['team'] = list(Membership.objects.filter(department_id__in=ids).values('user__username', 'department__name', 'availability', 'is_manager'))
        if has_permission(user, 'report.view.university'):
            users = get_user_model().objects
            result['university'] = {'students': users.filter(role='student').count(), 'active_students': users.filter(role='student', is_active=True).count(), 'employees': users.filter(role='support').count(), 'departments': Department.objects.filter(is_active=True).count(), 'tickets': Ticket.objects.count()}
        return Response(result)
