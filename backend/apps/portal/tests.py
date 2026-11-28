from datetime import datetime, time
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from .forms import validate_submission
from .models import Article, BusinessCalendar, Department, Holiday, RequestForm
from .search import normalize
from .sla import add_business_minutes, business_minutes_between
from .identity import issue_activation
from .models import Activation, Profile
from datetime import timedelta


class PublicContentTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.department = Department.objects.create(name='فناوری آزمایشی', slug='demo-it')

    def test_public_persian_search_filters_private_and_future_articles(self):
        Article.objects.create(title='شبکه دانشگاه', slug='network', content='راهنمای كاربري ۱۲۳ و ثبت‌نام', status='published', published_at=timezone.now(), department=self.department)
        Article.objects.create(title='Private', slug='private', content='ثبت نام 123', status='published', published_at=timezone.now(), is_public=False)
        Article.objects.create(title='Draft', slug='draft', content='ثبت نام 123')
        response = self.client.get('/api/v1/public/articles/', {'q': 'ثبت نام ١٢٣'})
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'شبکه دانشگاه')
        self.assertEqual(normalize('ي ك ۱ ٢ ثبت‌نام'), 'ی ک 1 2 ثبت نام')

    def test_guests_cannot_write_content_or_read_audit(self):
        self.assertEqual(self.client.get('/api/v1/public/').status_code, 200)
        self.assertEqual(self.client.get('/api/v1/public/departments/').status_code, 200)
        self.assertEqual(self.client.get(f'/api/v1/public/departments/{self.department.pk}/').status_code, 200)
        self.assertEqual(self.client.post('/api/v1/manage/departments/', {'name': 'Bad', 'slug': 'bad'}).status_code, 403)
        self.assertEqual(self.client.get('/api/v1/manage/audit/').status_code, 403)

    def test_admin_creates_department_and_category_without_source_changes(self):
        admin = get_user_model().objects.create_superuser('admin')
        self.client.force_authenticate(admin)
        metadata = self.client.get('/api/v1/manage/departments/form-metadata/')
        self.assertEqual(metadata.status_code, 200, metadata.data)
        self.assertIn('name', metadata.data['actions']['POST'])
        response = self.client.post('/api/v1/manage/departments/', {'name': 'واحد جدید', 'slug': 'new-unit'}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        pk = response.data['id']
        response = self.client.post('/api/v1/manage/categories/', {'name': 'دسته جدید', 'department': pk}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        response = self.client.patch(f'/api/v1/manage/departments/{pk}/', {'parent': pk}, format='json')
        self.assertEqual(response.status_code, 400)


class FormAndCalendarTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='واحد', slug='forms')

    def test_required_conditional_and_unknown_form_inputs(self):
        form = RequestForm.objects.create(name='فرم', department=self.department, fields=[{'key': 'service', 'label': 'خدمت', 'type': 'select', 'options': ['شبکه', 'حساب'], 'required': True}, {'key': 'device', 'label': 'دستگاه', 'type': 'text', 'required': True, 'visible_when': {'field': 'service', 'equals': 'شبکه'}}])
        with self.assertRaises(ValidationError):
            validate_submission(form, {'service': 'شبکه'})
        with self.assertRaises(ValidationError):
            validate_submission(form, {'service': 'حساب', 'extra': 'bad'})
        snapshot, answers = validate_submission(form, {'service': 'حساب'})
        form.fields = []
        form.save()
        self.assertEqual(len(snapshot['fields']), 2)
        self.assertEqual(answers, {'service': 'حساب'})

    def test_business_deadline_skips_holidays_weekend_and_after_hours(self):
        calendar = BusinessCalendar.objects.create(name='تهران', weekdays=[5, 6, 0, 1, 2], opens=time(8), closes=time(16))
        Holiday.objects.create(calendar=calendar, date='2026-11-29', name='تعطیل آزمایشی')
        zone = ZoneInfo('Asia/Tehran')
        start = datetime(2026, 11, 28, 15, 30, tzinfo=zone)
        end = add_business_minutes(start, 120, calendar)
        self.assertEqual(end, datetime(2026, 11, 30, 9, 30, tzinfo=zone))
        self.assertEqual(business_minutes_between(start, end, calendar), 120)
        after_hours = datetime(2026, 11, 25, 18, tzinfo=zone)
        self.assertEqual(add_business_minutes(after_hours, 60, calendar), datetime(2026, 11, 28, 9, tzinfo=zone))


class ActivationAndImportTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser('identity-admin')
        self.client = APIClient(enforce_csrf_checks=True)

    def test_activation_requires_issued_one_use_token_and_strong_password(self):
        user = get_user_model().objects.create_user('synthetic-student', is_active=False)
        Profile.objects.create(user=user, must_activate=True)
        token = issue_activation(self.admin, user)
        self.assertNotEqual(Activation.objects.get(user=user).digest, token)
        csrf = self.client.get('/api/v1/auth/csrf/').json()['csrfToken']
        path = '/api/v1/auth/activate/'
        payload = {'token': token, 'password': 'Strong-random-development-8472!'}
        self.assertEqual(self.client.post(path, payload, format='json').status_code, 403)
        self.assertEqual(self.client.post(path, {'token': token, 'password': '123'}, format='json', HTTP_X_CSRFTOKEN=csrf).status_code, 400)
        self.assertEqual(self.client.post(path, payload, format='json', HTTP_X_CSRFTOKEN=csrf).status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password(payload['password']))
        self.assertFalse(user.profile.must_activate)
        self.assertEqual(self.client.post(path, payload, format='json', HTTP_X_CSRFTOKEN=csrf).status_code, 400)

    def test_import_requires_preview_and_is_idempotent(self):
        self.client.force_authenticate(self.admin)
        upload = SimpleUploadedFile('students.csv', b'student_number,first_name,last_name,email\nDEMO100,Demo,Student,demo100@example.invalid\n', content_type='text/csv')
        response = self.client.post('/api/v1/manage/student-imports/', {'file': upload}, format='multipart')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertTrue(response.data['can_commit'])
        self.assertFalse(get_user_model().objects.filter(username='DEMO100').exists())
        path = f"/api/v1/manage/student-imports/{response.data['id']}/commit/"
        self.assertEqual(self.client.post(path).status_code, 200)
        self.assertEqual(self.client.post(path).status_code, 200)
        user = get_user_model().objects.get(username='DEMO100')
        self.assertFalse(user.is_active)
        self.assertFalse(user.has_usable_password())

    def test_duplicate_import_cannot_be_committed(self):
        self.client.force_authenticate(self.admin)
        upload = SimpleUploadedFile('students.csv', b'student_number,first_name,last_name,email\nDEMO1,A,B,demo@example.invalid\nDEMO1,C,D,demo2@example.invalid\n')
        response = self.client.post('/api/v1/manage/student-imports/', {'file': upload}, format='multipart')
        self.assertEqual(len(response.data['errors']), 1)
        self.assertEqual(self.client.post(f"/api/v1/manage/student-imports/{response.data['id']}/commit/").status_code, 400)
        self.assertFalse(get_user_model().objects.filter(username='DEMO1').exists())


class ScheduledWorkflowTests(TestCase):
    def test_monitor_is_idempotent_and_closes_only_expired_resolutions(self):
        from apps.ticketing.models import Category, Ticket
        from .models import Escalation, Membership, Notification, SLAPolicy
        from .tasks import monitor_service_levels
        user = get_user_model().objects.create_user('synthetic')
        manager = get_user_model().objects.create_user('manager', role='support')
        department = Department.objects.create(name='واحد پایش', slug='monitor')
        Membership.objects.create(user=manager, department=department, is_manager=True)
        calendar = BusinessCalendar.objects.create(name='کاری', weekdays=[0,1,2,3,4,5,6])
        policy = SLAPolicy.objects.create(name='تست', calendar=calendar)
        category = Category.objects.create(name='پایش', department=department, sla_policy=policy)
        ticket = Ticket.objects.create(created_by=user, category=category, department=department, title='Overdue', description='Synthetic', response_due_at=timezone.now() - timedelta(minutes=5))
        expired = Ticket.objects.create(created_by=user, category=category, department=department, title='Expired', description='Synthetic', status='resolved', resolved_at=timezone.now() - timedelta(days=8))
        monitor_service_levels()
        monitor_service_levels()
        self.assertEqual(Escalation.objects.filter(ticket=ticket).count(), 1)
        self.assertEqual(Notification.objects.filter(user=manager, ticket=ticket).count(), 1)
        expired.refresh_from_db()
        self.assertEqual(expired.status, 'closed')
        self.assertEqual(expired.events.filter(action='closed').count(), 1)
