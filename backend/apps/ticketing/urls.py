from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import CategoryListView, MetricsView, TicketViewSet

router = DefaultRouter()
router.register('tickets', TicketViewSet, basename='ticket')
urlpatterns = [path('categories/', CategoryListView.as_view()), path('metrics/', MetricsView.as_view()), path('', include(router.urls))]
