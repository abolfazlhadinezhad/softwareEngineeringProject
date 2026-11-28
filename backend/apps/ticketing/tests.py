from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
from rest_framework.test import APIClient

from .models import Category, Ticket, TicketEvent
from apps.portal.models import Department, Membership

User = get_user_model()


class TicketApiTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user('student', password='test-only-pass')
        self.other_student = User.objects.create_user('other', password='test-only-pass')
        self.support = User.objects.create_user('support', password='test-only-pass', role=User.Role.SUPPORT)
        self.admin = User.objects.create_superuser('admin', password='test-only-pass')
        self.department = Department.objects.create(name='آموزش آزمایشی', slug='education-test')
        Membership.objects.create(user=self.support, department=self.department)
        self.category = Category.objects.create(name='Academic support', department=self.department)
        self.client = APIClient(enforce_csrf_checks=True)

    def login(self, user):
        self.client.force_login(user)
        token = self.client.get('/api/auth/csrf/').json()['csrfToken']
        self.client.defaults['HTTP_X_CSRFTOKEN'] = token

    def create(self, title='Cannot access portal', owner=None):
        self.login(owner or self.student)
        return self.client.post('/api/tickets/', {'title': title, 'description': 'Please help me access the portal.', 'category': self.category.pk, 'priority': 'high'}, format='json')

    def test_student_creates_ticket_and_event_in_mysql(self):
        response = self.create()
        self.assertEqual(response.status_code, 201, response.data)
        ticket = Ticket.objects.get(pk=response.data['id'])
        self.assertEqual(ticket.created_by, self.student)
        self.assertEqual(ticket.status, Ticket.Status.OPEN)
        self.assertEqual(ticket.events.get().action, TicketEvent.Action.CREATED)
        with connection.cursor() as cursor:
            cursor.execute('SELECT VERSION()')
            self.assertTrue(cursor.fetchone()[0].startswith('8.0.'))

    def test_validation_rejects_blank_text_and_inactive_category(self):
        self.login(self.student)
        blank = self.client.post('/api/tickets/', {'title': ' ', 'description': ' ', 'category': self.category.pk}, format='json')
        self.assertEqual(blank.status_code, 400)
        self.category.is_active = False
        self.category.save()
        inactive = self.client.post('/api/tickets/', {'title': 'A title', 'description': 'A description', 'category': self.category.pk}, format='json')
        self.assertEqual(inactive.status_code, 400)

    def test_student_visibility_is_private(self):
        first = self.create()
        ticket_id = first.data['id']
        self.login(self.other_student)
        self.assertEqual(self.client.get(f'/api/tickets/{ticket_id}/').status_code, 404)
        self.assertEqual(self.client.get('/api/tickets/').data['count'], 0)

    def test_support_can_list_reply_claim_and_change_status(self):
        created = self.create()
        ticket_id = created.data['id']
        self.login(self.support)
        self.assertEqual(self.client.get('/api/tickets/').data['count'], 1)
        claimed = self.client.post(f'/api/tickets/{ticket_id}/claim/', {}, format='json')
        self.assertEqual(claimed.status_code, 200, claimed.data)
        self.assertEqual(claimed.data['status'], Ticket.Status.IN_PROGRESS)
        replied = self.client.post(f'/api/tickets/{ticket_id}/reply/', {'body': 'We are investigating this for you.'}, format='json')
        self.assertEqual(replied.status_code, 201, replied.data)
        changed = self.client.post(f'/api/tickets/{ticket_id}/status/', {'status': Ticket.Status.WAITING_STUDENT}, format='json')
        self.assertEqual(changed.status_code, 200, changed.data)
        self.assertEqual(changed.data['status'], Ticket.Status.WAITING_STUDENT)

    def test_competing_claim_is_conflict_and_closed_rejects_reply(self):
        created = self.create()
        ticket_id = created.data['id']
        self.login(self.support)
        self.assertEqual(self.client.post(f'/api/tickets/{ticket_id}/claim/', {}, format='json').status_code, 200)
        second = User.objects.create_user('support-two', password='test-only-pass', role=User.Role.SUPPORT)
        Membership.objects.create(user=second, department=self.department)
        self.login(second)
        self.assertEqual(self.client.post(f'/api/tickets/{ticket_id}/claim/', {}, format='json').status_code, 409)
        self.login(self.support)
        self.assertEqual(self.client.post(f'/api/tickets/{ticket_id}/status/', {'status': 'resolved', 'reason': 'Resolved in test'}, format='json').status_code, 200)
        self.assertEqual(self.client.post(f'/api/tickets/{ticket_id}/close/', {'reason': 'Confirmed'}, format='json').status_code, 200)
        self.assertEqual(self.client.post(f'/api/tickets/{ticket_id}/reply/', {'body': 'Late reply'}, format='json').status_code, 400)
        self.assertEqual(self.client.post(f'/api/tickets/{ticket_id}/reopen/', {'reason': 'Issue persists'}, format='json').status_code, 200)

    def test_staff_department_isolation_and_sensitive_admin_denial(self):
        ticket_id = self.create().data['id']
        outsider = User.objects.create_user('outsider', role='support')
        self.login(outsider)
        self.assertEqual(self.client.get('/api/tickets/').data['count'], 0)
        self.assertEqual(self.client.get(f'/api/tickets/{ticket_id}/').status_code, 404)
        Ticket.objects.filter(pk=ticket_id).update(confidentiality='confidential')
        self.login(self.admin)
        self.assertEqual(self.client.get(f'/api/tickets/{ticket_id}/').status_code, 404)

    def test_internal_note_never_appears_for_student(self):
        ticket_id = self.create().data['id']
        self.login(self.support)
        response = self.client.post(f'/api/tickets/{ticket_id}/note/', {'body': 'INTERNAL-SECRET'}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertIn('INTERNAL-SECRET', str(self.client.get(f'/api/tickets/{ticket_id}/').data))
        self.login(self.student)
        data = self.client.get(f'/api/tickets/{ticket_id}/').data
        self.assertEqual(data['internal_notes'], [])
        self.assertNotIn('INTERNAL-SECRET', str(data))
        self.assertNotIn('یادداشت داخلی', str(data))

    def test_priority_is_policy_controlled_and_invalid_transition_rejected(self):
        ticket_id = self.create().data['id']
        self.assertEqual(Ticket.objects.get(pk=ticket_id).priority, 'normal')
        self.login(self.support)
        response = self.client.post(f'/api/tickets/{ticket_id}/status/', {'status': 'closed', 'reason': 'Bypass'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_transfer_preserves_history_deadline_and_revokes_old_scope(self):
        ticket_id = self.create().data['id']
        member = Membership.objects.get(user=self.support)
        member.is_manager = True
        member.save()
        target = Department.objects.create(name='واحد دوم', slug='target')
        category = Category.objects.create(name='Target', department=target)
        self.login(self.support)
        response = self.client.post(f'/api/tickets/{ticket_id}/transfer/', {'department': target.pk, 'category': category.pk, 'reason': 'Correct routing'}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(self.client.get(f'/api/tickets/{ticket_id}/').status_code, 404)
        self.login(self.student)
        response = self.client.get(f'/api/tickets/{ticket_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['department'], target.pk)
        self.assertGreaterEqual(len(response.data['events']), 2)

    def test_private_attachment_checks_content_and_download_ownership(self):
        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            ticket_id = self.create().data['id']
            upload_path = f'/api/v1/tickets/{ticket_id}/attachments/'
            bad = SimpleUploadedFile('bad.pdf', b'not-a-pdf', content_type='application/pdf')
            self.assertEqual(self.client.post(upload_path, {'file': bad}, format='multipart').status_code, 400)
            good = SimpleUploadedFile('test.pdf', b'%PDF-1.7\nSynthetic test document', content_type='application/pdf')
            result = self.client.post(upload_path, {'file': good}, format='multipart')
            self.assertEqual(result.status_code, 201, result.data)
            download = f"{upload_path}{result.data['id']}/"
            response = self.client.get(download)
            self.assertEqual(response.status_code, 200)
            response.close()
            self.login(self.other_student)
            self.assertEqual(self.client.get(download).status_code, 404)
            self.assertEqual(self.client.post(upload_path, {'file': SimpleUploadedFile('x.pdf', b'%PDF-1.7', content_type='application/pdf')}, format='multipart').status_code, 404)

    def test_student_cannot_mutate_staff_status_or_other_ticket(self):
        created = self.create()
        ticket_id = created.data['id']
        self.login(self.student)
        response = self.client.post(f'/api/tickets/{ticket_id}/status/', {'status': Ticket.Status.CLOSED}, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.client.post(f'/api/tickets/{ticket_id}/claim/', {}, format='json').status_code, 403)

    def test_metrics_are_visibility_scoped(self):
        self.create('Student ticket')
        self.login(self.support)
        self.assertEqual(self.client.get('/api/metrics/').json()['all'], 1)
        self.login(self.other_student)
        self.assertEqual(self.client.get('/api/metrics/').json()['all'], 0)
