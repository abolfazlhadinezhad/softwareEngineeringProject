import csv
import io

from django.core.cache import cache
from django.db import connection
from django.http import HttpResponse
from django.utils import timezone
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ticketing.services import visible_tickets
from .models import SiteSettings
from .permissions import audit, department_ids, has_permission, require


class SettingsSerializer(serializers.ModelSerializer):
    auto_close_days = serializers.IntegerField(min_value=1, max_value=365)
    reopen_days = serializers.IntegerField(min_value=1, max_value=90)

    class Meta:
        model = SiteSettings
        fields = ['university_name', 'site_title', 'contact_email', 'support_hours', 'auto_close_days', 'reopen_days']


@extend_schema(request=SettingsSerializer, responses=SettingsSerializer)
class SettingsView(APIView):
    def get(self, request):
        require(request.user, 'settings.manage')
        obj, _ = SiteSettings.objects.get_or_create(pk=1)
        return Response(SettingsSerializer(obj).data)

    def patch(self, request):
        require(request.user, 'settings.manage')
        obj, _ = SiteSettings.objects.get_or_create(pk=1)
        serializer = SettingsSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        audit(request.user, 'settings.update', obj.pk, fields=list(serializer.validated_data))
        return Response(serializer.data)


def service_status():
    database, redis, worker = False, False, False
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            database = cursor.fetchone()[0] == 1
    except Exception:
        pass
    try:
        cache.set('readiness:probe', True, 10)
        redis = cache.get('readiness:probe') is True
        from datetime import datetime, timedelta
        heartbeat = cache.get('worker:heartbeat')
        worker = bool(heartbeat and timezone.now() - datetime.fromisoformat(heartbeat) < timedelta(seconds=180))
    except Exception:
        pass
    return {'database': database, 'redis': redis, 'worker': worker}


@extend_schema(responses=OpenApiTypes.OBJECT)
class SystemHealthView(APIView):
    def get(self, request):
        require(request.user, 'settings.manage')
        return Response(service_status())


def safe_cell(value):
    value = str(value or '')
    return "'" + value if value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r', '\n')) else value


@extend_schema(responses=OpenApiTypes.BINARY)
class TicketExportView(APIView):
    def get(self, request):
        user = request.user
        global_access = has_permission(user, 'ticket.export')
        ids = department_ids(user, 'ticket.export')
        if not global_access and not ids:
            require(user, 'ticket.export')
        tickets = visible_tickets(user).order_by('pk')
        if not global_access:
            tickets = tickets.filter(department_id__in=ids)
        # Bounded synchronous operational export. Large report jobs remain a backlog task.
        if tickets.count() > 5000:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('این خروجی بیش از ۵۰۰۰ ردیف دارد؛ تولید گزارش بزرگ باید به‌صورت غیرهم‌زمان انجام شود.')
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['tracking_number', 'title', 'department', 'status', 'priority', 'created_at', 'first_response_at', 'resolved_at'])
        for ticket in tickets.iterator(chunk_size=200):
            writer.writerow([safe_cell(v) for v in [ticket.tracking_number, ticket.title, ticket.department.name if ticket.department else '', ticket.status, ticket.priority, ticket.created_at.isoformat(), ticket.first_response_at.isoformat() if ticket.first_response_at else '', ticket.resolved_at.isoformat() if ticket.resolved_at else '']])
        audit(user, 'ticket.export', 'csv', count=tickets.count())
        response = HttpResponse('\ufeff' + output.getvalue(), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="bnut-tickets.csv"'
        return response
