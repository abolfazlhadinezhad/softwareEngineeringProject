import csv
import hashlib
import io
import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model, logout, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import Activation, ImportBatch, Profile
from .permissions import audit, require

User = get_user_model()


def issue_activation(actor, user):
    require(actor, 'student.manage' if user.role == 'student' else 'employee.manage')
    token = secrets.token_urlsafe(32)
    Activation.objects.filter(user=user, used_at__isnull=True).update(used_at=timezone.now())
    Activation.objects.create(user=user, digest=hashlib.sha256(token.encode()).hexdigest(), expires_at=timezone.now() + timedelta(hours=24))
    audit(actor, 'account.activation_issued', user.pk)
    return token


class ActivationInput(serializers.Serializer):
    token = serializers.CharField(max_length=150, write_only=True)
    password = serializers.CharField(max_length=1024, write_only=True, trim_whitespace=False)


@method_decorator(csrf_protect, name='dispatch')
class ActivationView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    @transaction.atomic
    def post(self, request):
        serializer = ActivationInput(data=request.data)
        serializer.is_valid(raise_exception=True)
        digest = hashlib.sha256(serializer.validated_data['token'].encode()).hexdigest()
        activation = Activation.objects.select_for_update().filter(digest=digest, used_at__isnull=True, expires_at__gt=timezone.now()).first()
        if not activation:
            raise ValidationError('کد فعال‌سازی معتبر نیست یا منقضی شده است.')
        user = User.objects.select_for_update().get(pk=activation.user_id)
        try:
            validate_password(serializer.validated_data['password'], user)
        except DjangoValidationError as exc:
            raise ValidationError({'password': exc.messages})
        user.set_password(serializer.validated_data['password'])
        user.is_active = True
        user.save()
        Profile.objects.filter(user=user).update(must_activate=False)
        activation.used_at = timezone.now()
        activation.save(update_fields=['used_at'])
        audit(user, 'account.activated', user.pk)
        return Response({'success': True})


class IssueActivationView(APIView):
    @transaction.atomic
    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        user = get_object_or_404(User, pk=pk)
        # Issued credentials require controlled out-of-band distribution by university staff.
        return Response({'token': issue_activation(request.user, user), 'expires_in_hours': 24})


class ProfileView(APIView):
    def get(self, request):
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)
        return Response({'username': user.username, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'role': user.role, 'student_number': profile.student_number, 'faculty': profile.faculty, 'program': profile.program, 'degree': profile.degree, 'admission_year': profile.admission_year, 'notification_preferences': profile.notification_preferences})

    def patch(self, request):
        if set(request.data) != {'notification_preferences'} or not isinstance(request.data['notification_preferences'], dict) or any(k not in ('in_app', 'email', 'sms', 'push') or not isinstance(v, bool) for k, v in request.data['notification_preferences'].items()):
            raise ValidationError('فقط ترجیحات اعلان با مقدار بله یا خیر قابل تغییر است.')
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.notification_preferences = request.data['notification_preferences']
        profile.save()
        return self.get(request)


class PasswordView(APIView):
    def post(self, request):
        if not request.user.check_password(str(request.data.get('current_password', ''))):
            raise PermissionDenied('رمز فعلی معتبر نیست.')
        password = request.data.get('password', '')
        if not isinstance(password, str) or len(password) > 1024:
            raise ValidationError('رمز معتبر نیست.')
        try:
            validate_password(password, request.user)
        except DjangoValidationError as exc:
            raise ValidationError({'password': exc.messages})
        request.user.set_password(password)
        request.user.save()
        update_session_auth_hash(request._request, request.user)
        audit(request.user, 'account.password_changed', request.user.pk)
        return Response({'success': True})


class StudentImportView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        require(request.user, 'student.manage')
        return Response(list(ImportBatch.objects.filter(actor=request.user).values('id', 'created_at', 'committed_at')[:50]))

    def post(self, request):
        require(request.user, 'student.manage')
        upload = request.FILES.get('file')
        if not upload or not upload.name.lower().endswith('.csv') or upload.size > 1024 * 1024:
            raise ValidationError('فایل CSV با کدگذاری UTF-8 و حداکثر یک مگابایت انتخاب کنید.')
        try:
            reader = csv.DictReader(io.StringIO(upload.read().decode('utf-8-sig')))
            required = {'student_number', 'first_name', 'last_name', 'email'}
            if not reader.fieldnames or set(reader.fieldnames) != required:
                raise ValidationError({'columns': 'ستون‌های دقیق: student_number, first_name, last_name, email. کد ملی و رمز مجاز نیست.'})
            rows, errors, seen = [], [], set()
            for index, row in enumerate(reader, 2):
                if index > 1001:
                    raise ValidationError('حداکثر ۱۰۰۰ دانشجو در هر ورود مجاز است.')
                student = row.get('student_number', '')
                error = None
                if not student or not student.isascii() or not student.isalnum() or len(student) > 30:
                    error = 'شماره دانشجویی معتبر نیست.'
                elif student in seen or User.objects.filter(username=student).exists() or Profile.objects.filter(student_number=student).exists():
                    error = 'شماره دانشجویی تکراری است.'
                elif not all(isinstance(row.get(key), str) and 0 < len(row[key]) <= (254 if key == 'email' else 150) for key in required):
                    error = 'ستون خالی یا طول نامعتبر است.'
                else:
                    try:
                        validate_email(row['email'])
                    except DjangoValidationError:
                        error = 'ایمیل معتبر نیست.'
                seen.add(student)
                rows.append(row)
                if error:
                    errors.append({'row': index, 'error': error})
        except (UnicodeError, csv.Error):
            raise ValidationError('فایل CSV قابل خواندن نیست.')
        batch = ImportBatch.objects.create(actor=request.user, rows=rows, errors=errors)
        audit(request.user, 'student.import_preview', batch.pk, rows=len(rows), errors=len(errors))
        return Response({'id': batch.pk, 'rows': rows[:20], 'total': len(rows), 'errors': errors, 'can_commit': bool(rows) and not errors}, status=201)


class StudentImportCommitView(APIView):
    @transaction.atomic
    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        require(request.user, 'student.manage')
        batch = get_object_or_404(ImportBatch.objects.select_for_update(), pk=pk, actor=request.user)
        if batch.committed_at:
            return Response({'id': pk, 'imported': len(batch.rows), 'already_committed': True})
        if batch.errors or not batch.rows or batch.created_at < timezone.now() - timedelta(hours=24):
            raise ValidationError('پیش‌نمایش دارای خطا، خالی یا منقضی شده است.')
        from django.db import IntegrityError
        try:
            with transaction.atomic():
                for row in batch.rows:
                    user = User.objects.create_user(username=row['student_number'], first_name=row['first_name'], last_name=row['last_name'], email=row['email'], is_active=False)
                    Profile.objects.create(user=user, student_number=row['student_number'], must_activate=True)
        except IntegrityError:
            raise ValidationError('پس از پیش‌نمایش یک شماره تکراری ایجاد شده است؛ هیچ حسابی وارد نشد.')
        batch.committed_at = timezone.now()
        batch.save(update_fields=['committed_at'])
        audit(request.user, 'student.import_committed', pk, count=len(batch.rows))
        return Response({'id': pk, 'imported': len(batch.rows)})
