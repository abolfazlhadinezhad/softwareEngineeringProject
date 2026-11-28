from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import identity

router = DefaultRouter()
for prefix, view in [
    ('departments', views.DepartmentViewSet), ('categories', views.CategoryViewSet),
    ('forms', views.FormViewSet), ('roles', views.RoleViewSet),
    ('role-assignments', views.RoleAssignmentViewSet), ('memberships', views.MembershipViewSet),
    ('calendars', views.CalendarViewSet), ('holidays', views.HolidayViewSet), ('sla-policies', views.SLAViewSet),
    ('articles', views.ArticleViewSet), ('faqs', views.FAQViewSet), ('announcements', views.AnnouncementViewSet),
]:
    router.register('manage/' + prefix, view, basename='manage-' + prefix)

urlpatterns = [
    path('auth/activate/', identity.ActivationView.as_view()),
    path('profile/', identity.ProfileView.as_view()),
    path('auth/password/', identity.PasswordView.as_view()),
    path('manage/users/<int:pk>/activation/', identity.IssueActivationView.as_view()),
    path('manage/student-imports/', identity.StudentImportView.as_view()),
    path('manage/student-imports/<int:pk>/commit/', identity.StudentImportCommitView.as_view()),
    path('public/', views.PublicView.as_view()),
    path('public/<str:resource>/', views.PublicView.as_view()),
    path('public/<str:resource>/<int:pk>/', views.PublicView.as_view()),
    path('notifications/', views.NotificationView.as_view()),
    path('tickets/<int:pk>/feedback/', views.FeedbackView.as_view()),
    path('manage/permissions/', views.PermissionCatalogView.as_view()),
    path('manage/audit/', views.AuditView.as_view()),
    path('', include(router.urls)),
]
