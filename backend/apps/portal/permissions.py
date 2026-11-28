from django.db.models import Q
from rest_framework.exceptions import PermissionDenied

from .models import RoleAssignment

PERMISSIONS = [
    'ticket.create', 'ticket.view.own', 'ticket.view.assigned', 'ticket.view.department',
    'ticket.view.all', 'ticket.view.confidential', 'ticket.reply', 'ticket.assign',
    'ticket.transfer', 'ticket.change_priority', 'ticket.resolve', 'ticket.close',
    'ticket.reopen', 'ticket.export', 'ticket.add_internal_note', 'department.manage',
    'employee.manage', 'student.manage', 'role.manage', 'permission.manage',
    'report.view.department', 'report.view.university', 'knowledge_base.publish',
    'audit.view', 'settings.manage',
]

AGENT = ['ticket.view.assigned', 'ticket.view.department', 'ticket.reply', 'ticket.assign', 'ticket.resolve', 'ticket.close', 'ticket.reopen', 'ticket.add_internal_note']
MANAGER = AGENT + ['ticket.transfer', 'ticket.change_priority', 'ticket.export', 'report.view.department']


def has_permission(user, permission, department_id=None):
    if not user.is_authenticated or not user.is_active:
        return False
    # Platform administrators manage configuration; confidential access remains explicit.
    if user.role == 'admin' and permission != 'ticket.view.confidential':
        return True
    if user.role == 'student':
        return permission in ['ticket.create', 'ticket.view.own', 'ticket.reply', 'ticket.close', 'ticket.reopen']
    assignments = RoleAssignment.objects.filter(user=user)
    assignments = assignments.filter(department__isnull=True) if department_id is None else assignments.filter(Q(department__isnull=True) | Q(department_id=department_id))
    if any(permission in assignment.role.permissions for assignment in assignments.select_related('role')):
        return True
    if department_id is not None:
        membership = user.memberships.filter(department_id=department_id).first()
        if membership:
            return permission in (MANAGER if membership.is_manager else AGENT)
    return False


def require(user, permission, department_id=None):
    if not has_permission(user, permission, department_id):
        raise PermissionDenied('مجوز انجام این عملیات را ندارید.')


def department_ids(user, permission='ticket.view.department'):
    from .models import Department
    return [pk for pk in Department.objects.values_list('pk', flat=True) if has_permission(user, permission, pk)]


def audit(actor, action, resource, department=None, **details):
    from .models import AuditLog
    return AuditLog.objects.create(actor=actor, action=action, resource=str(resource), department=department, details=details)
