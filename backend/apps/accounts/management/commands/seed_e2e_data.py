import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.ticketing.models import Category
from django.utils import timezone
from apps.portal.models import Department, Membership, Article, FAQ, Announcement, BusinessCalendar, SLAPolicy, RequestForm


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
            ('e2e_manager', user_model.Role.SUPPORT),
            ('e2e_admin', user_model.Role.ADMIN),
        ):
            user, _ = user_model.objects.get_or_create(username=username, defaults={'role': role})
            user.role = role
            user.is_active = True
            user.set_password(password)
            user.save()

        department, _ = Department.objects.get_or_create(slug='demo-it', defaults={'name': 'فناوری اطلاعات (آزمایشی)', 'description': 'داده نمایشی؛ ساختار رسمی دانشگاه نیست.', 'business_hours': 'شنبه تا چهارشنبه، ۸ تا ۱۶'})
        calendar, _ = BusinessCalendar.objects.get_or_create(name='تقویم نمایشی', defaults={'weekdays': [5, 6, 0, 1, 2]})
        sla, _ = SLAPolicy.objects.get_or_create(name='پاسخگویی نمایشی', defaults={'calendar': calendar})
        form, _ = RequestForm.objects.get_or_create(name='پشتیبانی فناوری (آزمایشی)', department=department, defaults={'fields': [{'key': 'service', 'label': 'خدمت مورد نظر', 'type': 'select', 'options': ['اینترنت', 'حساب دانشگاهی'], 'required': True}]})
        Category.objects.update_or_create(name='Browser test support', defaults={'is_active': True, 'department': department, 'sla_policy': sla, 'form': form})
        for username in ['e2e_support', 'e2e_manager']:
            Membership.objects.update_or_create(user=user_model.objects.get(username=username), department=department, defaults={'is_manager': username == 'e2e_manager'})
        Article.objects.update_or_create(slug='demo-network-help', defaults={'title': 'راهنمای اتصال به اینترنت دانشگاه (نمایشی)', 'summary': 'گام‌های بررسی اتصال و ثبت درخواست پشتیبانی.', 'content': 'ابتدا اتصال شبکه دستگاه خود را بررسی کنید. هرگز رمز حساب خود را در درخواست پشتیبانی وارد نکنید. اگر مشکل ادامه داشت، نام خدمت و زمان رخداد را در درخواست بنویسید.', 'department': department, 'status': 'published', 'published_at': timezone.now(), 'category': 'فناوری اطلاعات', 'tags': ['اینترنت', 'شبکه']})
        FAQ.objects.update_or_create(question='چگونه وضعیت درخواست خود را پیگیری کنم؟', defaults={'answer': 'پس از ورود به حساب دانشجویی، بخش درخواست‌های من را باز کنید. پاسخ‌ها و تاریخچه رسیدگی در صفحه درخواست نمایش داده می‌شود.', 'category': 'راهنمای سامانه', 'is_published': True})
        Announcement.objects.update_or_create(title='نسخه نمایشی سامانه پشتیبانی', defaults={'content': 'همه حساب‌ها و اطلاعات این نسخه ساختگی هستند. این اطلاعیه تأیید رسمی دانشگاه نیست.', 'is_published': True, 'starts_at': timezone.now(), 'pinned': True})
        self.stdout.write(self.style.SUCCESS('Disposable browser-test identities and category are ready.'))
