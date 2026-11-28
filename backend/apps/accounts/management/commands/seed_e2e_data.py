import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.ticketing.models import Category


class Command(BaseCommand):
    help = 'Create disposable browser-test accounts and a support category (development only).'

    def handle(self, *args, **options):
        password = os.environ.get('E2E_TEST_PASSWORD', '')
        if os.environ.get('DJANGO_DEBUG', '').lower() != 'true':
            raise CommandError('Browser test identities are available only when DJANGO_DEBUG=true.')
        if len(password) < 16:
            raise CommandError('Set E2E_TEST_PASSWORD to a random value of at least 16 characters.')

        user_model = get_user_model()
        for username, role in (
            ('e2e_student', user_model.Role.STUDENT),
            ('e2e_other_student', user_model.Role.STUDENT),
            ('e2e_support', user_model.Role.SUPPORT),
        ):
            user, _ = user_model.objects.get_or_create(username=username, defaults={'role': role})
            user.role = role
            user.is_active = True
            user.set_password(password)
            user.save()

        Category.objects.get_or_create(name='Browser test support', defaults={'is_active': True})
        self.stdout.write(self.style.SUCCESS('Disposable browser-test identities and category are ready.'))
