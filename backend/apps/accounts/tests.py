from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase

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
