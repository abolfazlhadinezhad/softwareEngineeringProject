from django.contrib import admin
from django.db import connection
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
    except Exception:
        return JsonResponse({'status': 'unavailable'}, status=503)
    return JsonResponse({'status': 'ok'})


def liveness(request):
    return JsonResponse({'status': 'ok'})


def readiness(request):
    from apps.portal.operations import service_status
    status = service_status()
    ready = status['database'] and status['redis']
    return JsonResponse({'status': 'ready' if ready else 'unavailable'}, status=200 if ready else 503)


urlpatterns = [
    path('api/v1/health/live/', liveness),
    path('api/v1/health/ready/', readiness),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/', include('apps.portal.urls')),
    path('api/v1/', include('apps.ticketing.urls')),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/', include('apps.ticketing.urls')),
    path('admin/', admin.site.urls),
    path('api/health/', health),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
