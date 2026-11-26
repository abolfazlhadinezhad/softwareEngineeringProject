from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class AccountManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields['role'] = User.Role.ADMIN
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        SUPPORT = 'support', 'Support staff'
        ADMIN = 'admin', 'Administrator'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    objects = AccountManager()

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(role__in=['student', 'support', 'admin']), name='valid_user_role')]

    def save(self, *args, **kwargs):
        self.is_staff = self.role == self.Role.ADMIN
        if not self.is_staff:
            self.is_superuser = False
        if kwargs.get('update_fields') is not None:
            kwargs['update_fields'] = set(kwargs['update_fields']) | {'is_staff', 'is_superuser'}
        return super().save(*args, **kwargs)
