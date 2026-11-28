from django.db.models import Count
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .filters import TicketFilter
from .models import Category, Ticket
from .serializers import CategorySerializer, ReplyCreateSerializer, ReplySerializer, StatusSerializer, TicketCreateSerializer, TicketDetailSerializer, TicketListSerializer
from .services import add_reply, change_status, claim_ticket, create_ticket, release_ticket, student_close, student_reopen, visible_tickets


class CategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=CategorySerializer(many=True))
    def get(self, request):
        return Response(CategorySerializer(Category.objects.filter(is_active=True), many=True).data)


@extend_schema_view(
    list=extend_schema(parameters=[OpenApiParameter('search', str, description='Search title and description'), OpenApiParameter('status', str), OpenApiParameter('priority', str), OpenApiParameter('category', int), OpenApiParameter('page', int)]),
    create=extend_schema(request=TicketCreateSerializer, responses=TicketDetailSerializer),
)
class TicketViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Ticket.objects.none()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TicketFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'status']
    ordering = ['-updated_at', '-id']

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.queryset
        queryset = visible_tickets(self.request.user)
        if self.action == 'retrieve':
            return queryset.prefetch_related('replies__author', 'events__actor')
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return TicketCreateSerializer
        if self.action == 'retrieve':
            return TicketDetailSerializer
        if self.action == 'reply':
            return ReplyCreateSerializer
        if self.action == 'status':
            return StatusSerializer
        return TicketListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = TicketListSerializer(page if page is not None else queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        ticket = self.get_object()
        return Response(TicketDetailSerializer(ticket).data)

    def create(self, request, *args, **kwargs):
        if request.user.role != 'student':
            return Response({'error': {'status': 403, 'details': {'detail': 'Only students can submit tickets.'}}}, status=403)
        serializer = TicketCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = create_ticket(actor=request.user, **serializer.validated_data)
        return Response(TicketDetailSerializer(ticket).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        ticket = self.get_object()
        serializer = ReplyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reply = add_reply(ticket=ticket, actor=request.user, **serializer.validated_data)
        return Response(ReplySerializer(reply).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        ticket = self.get_object()
        return Response(TicketDetailSerializer(claim_ticket(ticket=ticket, actor=request.user)).data)

    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        ticket = self.get_object()
        return Response(TicketDetailSerializer(release_ticket(ticket=ticket, actor=request.user)).data)

    @action(detail=True, methods=['post'])
    def status(self, request, pk=None):
        ticket = self.get_object()
        serializer = StatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(TicketDetailSerializer(change_status(ticket=ticket, actor=request.user, **serializer.validated_data)).data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        ticket = self.get_object()
        if request.user.role in ('support', 'admin'):
            result = change_status(ticket=ticket, actor=request.user, status=Ticket.Status.CLOSED)
        else:
            result = student_close(ticket=ticket, actor=request.user)
        return Response(TicketDetailSerializer(result).data)

    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        ticket = self.get_object()
        if request.user.role in ('support', 'admin'):
            result = change_status(ticket=ticket, actor=request.user, status=Ticket.Status.OPEN)
        else:
            result = student_reopen(ticket=ticket, actor=request.user)
        return Response(TicketDetailSerializer(result).data)


class MetricsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=dict)
    def get(self, request):
        counts = visible_tickets(request.user).values('status').annotate(count=Count('id'))
        by_status = {item['status']: item['count'] for item in counts}
        return Response({'all': sum(by_status.values()), 'active': sum(value for key, value in by_status.items() if key != Ticket.Status.CLOSED), 'closed': by_status.get(Ticket.Status.CLOSED, 0), 'by_status': by_status})
