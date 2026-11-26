from django.urls import path
from .views import LoginView, LogoutView, SessionView, csrf

urlpatterns = [
    path('csrf/', csrf), path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()), path('me/', SessionView.as_view()),
]
