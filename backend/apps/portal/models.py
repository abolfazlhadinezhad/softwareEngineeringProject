import uuid

from django.conf import settings
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=150)
    english_name = models.CharField(max_length=150, blank=True)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, related_name='children')
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=40, default='building')
    color = models.CharField(max_length=7, default='#234a78')
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    business_hours = models.CharField(max_length=250, blank=True)
    assignment_strategy = models.CharField(max_length=20, choices=[('manual', 'Manual'), ('least_active', 'Least active'), ('round_robin', 'Round robin')], default='manual')
    last_assignee_id = models.PositiveBigIntegerField(default=0)
    confidentiality = models.CharField(max_length=20, default='normal', choices=[('normal', 'Normal'), ('restricted', 'Restricted'), ('confidential', 'Confidential')])

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class AccessRole(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    permissions = models.JSONField(default=list)
    description = models.TextField(blank=True)


class RoleAssignment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='access_roles')
    role = models.ForeignKey(AccessRole, on_delete=models.PROTECT, related_name='assignments')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)


class Membership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='memberships')
    is_manager = models.BooleanField(default=False)
    availability = models.CharField(max_length=20, default='available', choices=[('available', 'Available'), ('busy', 'Busy'), ('offline', 'Offline'), ('leave', 'On leave')])
    job_title = models.CharField(max_length=100, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'department'], name='unique_department_member')]


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    student_number = models.CharField(max_length=30, unique=True, null=True, blank=True)
    employee_number = models.CharField(max_length=30, blank=True)
    faculty = models.CharField(max_length=150, blank=True)
    program = models.CharField(max_length=150, blank=True)
    degree = models.CharField(max_length=50, blank=True)
    admission_year = models.PositiveIntegerField(null=True, blank=True)
    notification_preferences = models.JSONField(default=dict)
    must_activate = models.BooleanField(default=False)
    # MFA enrollment belongs in an encrypted credential store, never in this profile.


class Activation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    digest = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)


class BusinessCalendar(models.Model):
    name = models.CharField(max_length=100)
    timezone = models.CharField(max_length=50, default='Asia/Tehran')
    weekdays = models.JSONField(default=list)
    opens = models.TimeField(default='08:00')
    closes = models.TimeField(default='16:00')


class Holiday(models.Model):
    calendar = models.ForeignKey(BusinessCalendar, on_delete=models.CASCADE, related_name='holidays')
    date = models.DateField()
    name = models.CharField(max_length=100)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['calendar', 'date'], name='unique_calendar_holiday')]


class SLAPolicy(models.Model):
    name = models.CharField(max_length=100)
    calendar = models.ForeignKey(BusinessCalendar, on_delete=models.PROTECT)
    first_response_minutes = models.PositiveIntegerField(default=240)
    resolution_minutes = models.PositiveIntegerField(default=1440)
    warning_minutes = models.PositiveIntegerField(default=60)
    pause_waiting_student = models.BooleanField(default=True)


class RequestForm(models.Model):
    name = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    version = models.PositiveIntegerField(default=1)
    fields = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)


class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, allow_unicode=True)
    summary = models.TextField(blank=True)
    content = models.TextField()
    category = models.CharField(max_length=100, default='راهنمای عمومی')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)
    tags = models.JSONField(default=list)
    related = models.ManyToManyField('self', blank=True)
    status = models.CharField(max_length=15, default='draft', choices=[('draft', 'Draft'), ('review', 'Review'), ('published', 'Published'), ('archived', 'Archived')])
    is_public = models.BooleanField(default=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    helpful = models.PositiveIntegerField(default=0)
    unhelpful = models.PositiveIntegerField(default=0)
    search_text = models.TextField(blank=True)

    class Meta:
        ordering = ['-updated_at']

    def save(self, *args, **kwargs):
        from .search import normalize
        self.search_text = normalize(f'{self.title} {self.summary} {self.content} {" ".join(self.tags)}')
        super().save(*args, **kwargs)


class ArticleRevision(models.Model):
    article = models.ForeignKey(Article, on_delete=models.PROTECT, related_name='revisions')
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)


class FAQ(models.Model):
    question = models.CharField(max_length=250)
    answer = models.TextField()
    category = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True, blank=True)
    is_published = models.BooleanField(default=False)
    ordering = models.PositiveIntegerField(default=0)
    helpful = models.PositiveIntegerField(default=0)
    unhelpful = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordering', 'id']


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)
    priority = models.CharField(max_length=20, default='normal', choices=[('normal', 'Normal'), ('important', 'Important'), ('urgent', 'Urgent')])
    audience = models.CharField(max_length=20, default='public', choices=[('public', 'Public'), ('student', 'Student'), ('staff', 'Staff')])
    is_published = models.BooleanField(default=False)
    pinned = models.BooleanField(default=False)
    starts_at = models.DateTimeField()
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-pinned', '-starts_at']


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=40, default='ticket')
    ticket = models.ForeignKey('ticketing.Ticket', on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    idempotency_key = models.CharField(max_length=150, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class AccessGrant(models.Model):
    ticket = models.ForeignKey('ticketing.Ticket', on_delete=models.CASCADE, related_name='access_grants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    expires_at = models.DateTimeField()


class Feedback(models.Model):
    ticket = models.OneToOneField('ticketing.Ticket', on_delete=models.PROTECT, related_name='feedback')
    overall = models.PositiveSmallIntegerField()
    speed = models.PositiveSmallIntegerField()
    quality = models.PositiveSmallIntegerField()
    solved = models.BooleanField(default=True)
    comment = models.TextField(blank=True, max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)


class Escalation(models.Model):
    ticket = models.ForeignKey('ticketing.Ticket', on_delete=models.PROTECT, related_name='escalations')
    trigger = models.CharField(max_length=50)
    level = models.PositiveIntegerField(default=1)
    reason = models.TextField()
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['ticket', 'trigger', 'level'], name='unique_escalation_trigger')]


class ResponseTemplate(models.Model):
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    title = models.CharField(max_length=150)
    body = models.TextField()
    is_active = models.BooleanField(default=True)


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    details = models.JSONField(default=dict)
    correlation_id = models.UUIDField(default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class ImportBatch(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    rows = models.JSONField(default=list)
    errors = models.JSONField(default=list)
    committed_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class SiteSettings(models.Model):
    university_name = models.CharField(max_length=200, default='دانشگاه صنعتی نوشیروانی بابل')
    site_title = models.CharField(max_length=200, default='سامانه پشتیبانی دانشجویان')
    contact_email = models.EmailField(blank=True)
    support_hours = models.CharField(max_length=200, default='شنبه تا چهارشنبه، ۸ تا ۱۶')
    auto_close_days = models.PositiveIntegerField(default=7)
    reopen_days = models.PositiveIntegerField(default=14)
    maintenance_mode = models.BooleanField(default=False)


class SearchGap(models.Model):
    query_hash = models.CharField(max_length=64, unique=True)
    count = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)
