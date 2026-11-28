from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    capabilities = serializers.SerializerMethodField()
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name', 'last_name', 'role', 'capabilities']
        read_only_fields = fields

    def get_capabilities(self, user) -> list[str]:
        from apps.portal.permissions import PERMISSIONS, department_ids, has_permission
        return [p for p in PERMISSIONS if has_permission(user, p) or department_ids(user, p)]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=1024)
    portal = serializers.ChoiceField(choices=['student', 'staff', 'admin'], required=False)
