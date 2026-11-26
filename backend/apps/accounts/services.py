from django.contrib.auth import authenticate, login
from rest_framework.exceptions import PermissionDenied


def sign_in(*, request, username, password):
    user = authenticate(request=request, username=username, password=password)
    if user is None:
        raise PermissionDenied('Invalid username or password.')
    login(request, user)
    return user
