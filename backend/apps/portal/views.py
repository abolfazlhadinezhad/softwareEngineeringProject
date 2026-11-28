import hashlib

from django.core.cache import cache
from django.db import transaction
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiTypes, extend_schema

from apps.ticketing.models import Category
from apps.ticketing.serializers import CategorySerializer
from apps.ticketing.services import visible_tickets
from .models import AccessRole, Announcement, Article, ArticleRevision, AuditLog, BusinessCalendar, Department, FAQ, Feedback, Holiday, Membership, Notification, RequestForm, RoleAssignment, SiteSettings, SLAPolicy
from .permissions import PERMISSIONS, audit, department_ids, has_permission, require
from .search import normalize
from .serializers import AnnouncementSerializer, ArticleSerializer, CalendarSerializer, CategoryAdminSerializer, DepartmentSerializer, FAQSerializer, FormSerializer, HolidaySerializer, MembershipSerializer, RoleAssignmentSerializer, RoleSerializer, SLASerializer
from .serializers import PublicArticleSerializer, PublicDepartmentSerializer


@extend_schema(responses=OpenApiTypes.OBJECT)
class PublicView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, resource='home', pk=None):
        if resource not in ('home', 'departments', 'articles', 'faqs', 'announcements'):
            from rest_framework.exceptions import NotFound
            raise NotFound('منبع مورد نظر پیدا نشد.')
        now = timezone.now()
        departments = Department.objects.filter(is_active=True, is_public=True)
        articles = Article.objects.filter(status='published', is_public=True, published_at__lte=now).filter(Q(department__isnull=True) | Q(department__is_active=True, department__is_public=True))
        faqs = FAQ.objects.filter(is_published=True).filter(Q(department__isnull=True) | Q(department__is_active=True, department__is_public=True))
        announcements = Announcement.objects.filter(is_published=True, audience='public', starts_at__lte=now).filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now)).filter(Q(department__isnull=True) | Q(department__is_active=True, department__is_public=True))
        if resource == 'departments':
            if pk:
                department = get_object_or_404(departments, pk=pk)
                return Response({'department': PublicDepartmentSerializer(department).data, 'categories': CategorySerializer(Category.objects.filter(department=department, is_active=True).select_related('form'), many=True).data, 'articles': PublicArticleSerializer(articles.filter(department=department), many=True).data, 'faqs': FAQSerializer(faqs.filter(department=department), many=True).data})
            return Response(PublicDepartmentSerializer(departments, many=True).data)
        if resource == 'articles':
            if pk:
                article = get_object_or_404(articles, pk=pk)
                Article.objects.filter(pk=pk).update(views=F('views') + 1)
                data = PublicArticleSerializer(article).data
                data['related'] = list(articles.filter(pk__in=article.related.values('pk')).values('id', 'title', 'summary'))
                return Response(data)
            query = normalize(request.query_params.get('q', ''))[:120]
            for term in query.split()[:8]:
                articles = articles.filter(search_text__contains=term)
            for field in ['department', 'category']:
                value = request.query_params.get(field)
                if value:
                    if field == 'department' and not value.isdigit():
                        raise ValidationError({'department': 'شناسه واحد معتبر نیست.'})
                    articles = articles.filter(**{field: value})
            from rest_framework.pagination import PageNumberPagination
            pager = PageNumberPagination()
            page = pager.paginate_queryset(articles, request)
            return pager.get_paginated_response(PublicArticleSerializer(page, many=True).data)
        if resource == 'faqs':
            return Response(FAQSerializer(faqs[:100], many=True).data)
        if resource == 'announcements':
            return Response(AnnouncementSerializer(get_object_or_404(announcements, pk=pk)).data if pk else AnnouncementSerializer(announcements[:50], many=True).data)
        # Only public, non-personal records are cached. Time-sensitive announcements remain live.
        key = 'bnut:public:home:v1'
        try:
            data = cache.get(key)
        except Exception:
            data = None
        if data is None:
            data = {'departments': PublicDepartmentSerializer(departments, many=True).data, 'articles': PublicArticleSerializer(articles[:6], many=True).data, 'faqs': FAQSerializer(faqs[:6], many=True).data}
            try:
                cache.set(key, data, 60)
            except Exception:
                pass
        settings, _ = SiteSettings.objects.get_or_create(pk=1)
        return Response({**data, 'announcements': AnnouncementSerializer(announcements[:4], many=True).data, 'settings': {'university_name': settings.university_name, 'site_title': settings.site_title, 'support_hours': settings.support_hours, 'contact_email': settings.contact_email}})


class ManagedViewSet(viewsets.ModelViewSet):
    required_permission = 'department.manage'
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']
    department_field = 'department_id'

    @extend_schema(responses=OpenApiTypes.OBJECT)
    @action(detail=False, methods=['get'], url_path='form-metadata')
    def form_metadata(self, request):
        if not has_permission(request.user, self.required_permission) and not department_ids(request.user, self.required_permission):
            require(request.user, self.required_permission)
        return Response({'actions': {'POST': self.metadata_class().get_serializer_info(self.get_serializer())}})

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return self.queryset.none()
        if has_permission(user, self.required_permission):
            return self.queryset.all()
        ids = department_ids(user, self.required_permission)
        return self.queryset.filter(**{self.department_field + '__in': ids}) if self.department_field else self.queryset.none()

    def _authorize(self, serializer):
        department = serializer.validated_data.get('department', getattr(serializer.instance, 'department', None))
        if serializer.Meta.model is Department:
            department = serializer.instance
        if self.department_field is None:
            department = None
        require(self.request.user, self.required_permission, department.pk if department else None)

    @transaction.atomic
    def perform_create(self, serializer):
        self._authorize(serializer)
        extra = {'author': self.request.user} if serializer.Meta.model is Article else {}
        obj = serializer.save(**extra)
        audit(self.request.user, obj._meta.label + '.create', obj.pk, getattr(obj, 'department', None))
        self._invalidate()

    @transaction.atomic
    def perform_update(self, serializer):
        self._authorize(serializer)
        obj = serializer.instance
        if isinstance(obj, Article):
            ArticleRevision.objects.create(article=obj, editor=self.request.user, title=obj.title, content=obj.content)
        if isinstance(obj, RequestForm):
            serializer.save(version=obj.version + 1)
        else:
            serializer.save()
        audit(self.request.user, obj._meta.label + '.update', obj.pk, getattr(obj, 'department', None))
        self._invalidate()

    def _invalidate(self):
        def invalidate():
            try:
                cache.delete('bnut:public:home:v1')
            except Exception:
                pass  # Cache outage cannot roll back a committed business operation.
        transaction.on_commit(invalidate)


def managed_view(name, model, serializer, permission, department_field='department_id'):
    return type(name, (ManagedViewSet,), {'queryset': model.objects.all().order_by('pk'), 'serializer_class': serializer, 'required_permission': permission, 'department_field': department_field})


DepartmentViewSet = managed_view('DepartmentViewSet', Department, DepartmentSerializer, 'department.manage', 'pk')
CategoryViewSet = managed_view('CategoryViewSet', Category, CategoryAdminSerializer, 'department.manage')
FormViewSet = managed_view('FormViewSet', RequestForm, FormSerializer, 'department.manage')
RoleViewSet = managed_view('RoleViewSet', AccessRole, RoleSerializer, 'role.manage', None)
RoleAssignmentViewSet = managed_view('RoleAssignmentViewSet', RoleAssignment, RoleAssignmentSerializer, 'role.manage', None)
MembershipViewSet = managed_view('MembershipViewSet', Membership, MembershipSerializer, 'employee.manage')
CalendarViewSet = managed_view('CalendarViewSet', BusinessCalendar, CalendarSerializer, 'settings.manage', None)
HolidayViewSet = managed_view('HolidayViewSet', Holiday, HolidaySerializer, 'settings.manage', None)
SLAViewSet = managed_view('SLAViewSet', SLAPolicy, SLASerializer, 'settings.manage', None)
ArticleViewSet = managed_view('ArticleViewSet', Article, ArticleSerializer, 'knowledge_base.publish')
FAQViewSet = managed_view('FAQViewSet', FAQ, FAQSerializer, 'knowledge_base.publish')
AnnouncementViewSet = managed_view('AnnouncementViewSet', Announcement, AnnouncementSerializer, 'knowledge_base.publish')


@extend_schema(request=OpenApiTypes.OBJECT, responses=OpenApiTypes.OBJECT)
class NotificationView(APIView):
    def get(self, request):
        accessible = visible_tickets(request.user).values('pk')
        qs = Notification.objects.filter(user=request.user).filter(Q(ticket__isnull=True) | Q(ticket_id__in=accessible))
        return Response({'unread': qs.filter(is_read=False).count(), 'results': list(qs[:100].values('id', 'title', 'category', 'ticket_id', 'is_read', 'created_at'))})

    def post(self, request):
        qs = Notification.objects.filter(user=request.user)
        if request.data.get('id'):
            qs = qs.filter(pk=request.data['id'])
        qs.update(is_read=True)
        return Response({'success': True})


class FeedbackInput(serializers.Serializer):
    overall = serializers.IntegerField(min_value=1, max_value=5)
    speed = serializers.IntegerField(min_value=1, max_value=5)
    quality = serializers.IntegerField(min_value=1, max_value=5)
    solved = serializers.BooleanField(default=True)
    comment = serializers.CharField(max_length=2000, allow_blank=True, default='')


@extend_schema(request=FeedbackInput, responses=OpenApiTypes.OBJECT)
class FeedbackView(APIView):
    @transaction.atomic
    def post(self, request, pk):
        ticket = get_object_or_404(visible_tickets(request.user).select_for_update(), pk=pk, created_by=request.user, status__in=['resolved', 'closed'])
        serializer = FeedbackInput(data=request.data)
        serializer.is_valid(raise_exception=True)
        if Feedback.objects.filter(ticket=ticket).exists():
            raise ValidationError('برای این درخواست قبلاً ارزیابی ثبت شده است.')
        Feedback.objects.create(ticket=ticket, **serializer.validated_data)
        return Response({'success': True}, status=201)


@extend_schema(responses=OpenApiTypes.OBJECT)
class PermissionCatalogView(APIView):
    def get(self, request):
        require(request.user, 'role.manage')
        return Response(PERMISSIONS)


@extend_schema(responses=OpenApiTypes.OBJECT)
class AuditView(APIView):
    def get(self, request):
        require(request.user, 'audit.view')
        from rest_framework.pagination import PageNumberPagination
        pager = PageNumberPagination()
        records = pager.paginate_queryset(AuditLog.objects.all(), request)
        return pager.get_paginated_response([{'id': row.pk, 'actor': row.actor_id, 'action': row.action, 'resource': row.resource, 'department': row.department_id, 'created_at': row.created_at, 'correlation_id': row.correlation_id} for row in records])


