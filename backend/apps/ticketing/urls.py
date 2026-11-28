from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import CategoryListView, MetricsView, TicketViewSet
from .attachments import AttachmentView

router = DefaultRouter()
router.register('tickets', TicketViewSet, basename='ticket')
urlpatterns = [path('tickets/<int:pk>/attachments/', AttachmentView.as_view()), path('tickets/<int:pk>/attachments/<int:attachment_id>/', AttachmentView.as_view()), path('categories/', CategoryListView.as_view()), path('metrics/', MetricsView.as_view()), path('', include(router.urls))]
