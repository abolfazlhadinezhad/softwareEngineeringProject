from django.contrib.auth import authenticate, login
from rest_framework.exceptions import PermissionDenied


def sign_in(*, request, username, password, portal=None):
    user = authenticate(request=request, username=username, password=password)
    if user is None or (portal == 'student' and user.role != 'student') or (portal == 'staff' and user.role != 'support') or (portal == 'admin' and user.role != 'admin'):
        raise PermissionDenied('Invalid username or password.')
    if hasattr(user, 'profile') and user.profile.must_activate:
        raise PermissionDenied('Invalid username or password.')
    login(request, user)
    from apps.portal.permissions import audit
    audit(user, 'account.login', user.pk)
    return user
