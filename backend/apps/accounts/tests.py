from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.core.cache import cache
from rest_framework.test import APIClient

User = get_user_model()


class FoundationTests(TestCase):
    def test_real_mysql_eight_database(self):
        self.assertEqual(connection.vendor, 'mysql')
        with connection.cursor() as cursor:
            cursor.execute('SELECT VERSION()')
            self.assertTrue(cursor.fetchone()[0].startswith('8.0.'))

    def test_database_health(self):
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})

    def test_support_role_has_no_admin_console_access(self):
        user = User.objects.create_user('support', password='test-only-pass', role=User.Role.SUPPORT, is_staff=True)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password('test-only-pass'))
        self.assertNotEqual(user.password, 'test-only-pass')

    def test_superuser_has_administrator_role(self):
        user = User.objects.create_superuser('administrator', password='test-only-pass')
        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertTrue(user.is_staff)


class AuthenticationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user('student', password='test-only-pass')
        self.client = APIClient(enforce_csrf_checks=True)

    def token(self):
        return self.client.get('/api/auth/csrf/').json()['csrfToken']

    def test_login_requires_csrf_even_for_anonymous(self):
        response = self.client.post('/api/auth/login/', {'username': 'student', 'password': 'test-only-pass'}, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json())

    def test_login_session_logout_flow(self):
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 403)
        response = self.client.post('/api/auth/login/', {'username': 'student', 'password': 'test-only-pass'}, format='json', HTTP_X_CSRFTOKEN=self.token())
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('password', response.json())
        self.assertEqual(self.client.get('/api/auth/me/').json()['role'], 'student')
        self.assertEqual(self.client.get('/api/auth/me/')['Cache-Control'], 'no-store')
        self.assertEqual(self.client.post('/api/auth/logout/').status_code, 403)
        self.assertEqual(self.client.post('/api/auth/logout/', HTTP_X_CSRFTOKEN=self.token()).status_code, 204)
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 403)

    def test_disabled_and_wrong_credentials_are_rejected(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post('/api/auth/login/', {'username': 'student', 'password': 'test-only-pass'}, format='json', HTTP_X_CSRFTOKEN=self.token())
        self.assertEqual(response.status_code, 403)
        self.assertIn('Invalid username', str(response.json()))

    def test_support_cannot_enter_admin(self):
        self.user.role = 'support'
        self.user.save()
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/admin/').status_code, 302)
