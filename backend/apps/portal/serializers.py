from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from rest_framework import serializers

from apps.ticketing.models import Category
from .forms import validate_fields
from .models import AccessRole, Announcement, Article, BusinessCalendar, Department, FAQ, Holiday, Membership, RequestForm, RoleAssignment, SLAPolicy
from .permissions import PERMISSIONS


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        exclude = ['last_assignee_id']

    def validate_parent(self, parent):
        original = parent
        visited = set()
        while parent:
            if parent.pk in visited or self.instance and parent.pk == self.instance.pk:
                raise serializers.ValidationError('چرخه در ساختار واحدها مجاز نیست.')
            visited.add(parent.pk)
            parent = parent.parent
        return original

    def validate_color(self, value):
        import re
        if not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
            raise serializers.ValidationError('کد رنگ معتبر نیست.')
        return value


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRole
        fields = ['id', 'name', 'slug', 'permissions', 'description']

    def validate_permissions(self, value):
        if not isinstance(value, list) or not all(isinstance(p, str) and p in PERMISSIONS for p in value):
            raise serializers.ValidationError('مجوز ناشناخته است.')
        return sorted(set(value))


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestForm
        fields = ['id', 'name', 'department', 'version', 'fields', 'is_active']
        read_only_fields = ['version']

    def validate_fields(self, value):
        return validate_fields(value)


class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessCalendar
        fields = '__all__'

    def validate(self, attrs):
        opens = attrs.get('opens', getattr(self.instance, 'opens', None))
        closes = attrs.get('closes', getattr(self.instance, 'closes', None))
        days = attrs.get('weekdays', getattr(self.instance, 'weekdays', []))
        if not days or not isinstance(days, list) or any(type(x) is not int or x < 0 or x > 6 for x in days):
            raise serializers.ValidationError({'weekdays': 'روزهای کاری باید بین صفر (دوشنبه) و شش باشند.'})
        if opens and closes and opens >= closes:
            raise serializers.ValidationError({'closes': 'پایان ساعت کاری باید پس از شروع باشد.'})
        try:
            ZoneInfo(attrs.get('timezone', getattr(self.instance, 'timezone', 'Asia/Tehran')))
        except ZoneInfoNotFoundError:
            raise serializers.ValidationError({'timezone': 'منطقه زمانی معتبر نیست.'})
        return attrs


class CategoryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'department', 'parent', 'form', 'sla_policy', 'default_priority', 'is_active']

    def validate(self, attrs):
        department = attrs.get('department', getattr(self.instance, 'department', None))
        if not department:
            raise serializers.ValidationError({'department': 'واحد مسئول الزامی است.'})
        parent = attrs.get('parent', getattr(self.instance, 'parent', None))
        seen = set()
        cursor = parent
        while cursor:
            if cursor.pk in seen or self.instance and cursor.pk == self.instance.pk or cursor.department_id != department.pk:
                raise serializers.ValidationError({'parent': 'دسته والد باید از همان واحد و بدون چرخه باشد.'})
            seen.add(cursor.pk)
            cursor = cursor.parent
        form = attrs.get('form', getattr(self.instance, 'form', None))
        if form and form.department_id != department.pk:
            raise serializers.ValidationError({'form': 'فرم متعلق به این واحد نیست.'})
        return attrs


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        exclude = ['search_text']
        read_only_fields = ['author', 'views', 'helpful', 'unhelpful', 'updated_at']

    def validate_tags(self, value):
        if not isinstance(value, list) or len(value) > 20 or not all(isinstance(tag, str) and len(tag) <= 80 for tag in value):
            raise serializers.ValidationError('برچسب‌ها معتبر نیستند.')
        return value


def model_serializer(model, fields='__all__'):
    return type(model.__name__ + 'Serializer', (serializers.ModelSerializer,), {'Meta': type('Meta', (), {'model': model, 'fields': fields})})


FAQSerializer = model_serializer(FAQ)
AnnouncementSerializer = model_serializer(Announcement)
HolidaySerializer = model_serializer(Holiday)
SLASerializer = model_serializer(SLAPolicy)
MembershipSerializer = model_serializer(Membership)
RoleAssignmentSerializer = model_serializer(RoleAssignment)


class PublicDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'english_name', 'slug', 'parent', 'description', 'icon', 'color', 'email', 'phone', 'business_hours']


class PublicArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'summary', 'content', 'category', 'department', 'tags', 'published_at', 'updated_at', 'views', 'helpful', 'unhelpful']
