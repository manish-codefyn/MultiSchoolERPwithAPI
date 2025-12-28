
from rest_framework import serializers
from apps.auth.models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add custom user data
        user_data = {
            'id': str(self.user.id),
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
            'is_superuser': self.user.is_superuser,
        }
        
        if hasattr(self.user, 'tenant') and self.user.tenant:
            user_data['tenant'] = {
                'id': str(self.user.tenant.id),
                'name': self.user.tenant.name,
                'schema_name': self.user.tenant.schema_name
            }
            
        return {
            'tokens': data,
            'user': user_data
        }

class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = '__all__'

class APITokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIToken
        fields = '__all__'

class SecurityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEvent
        fields = '__all__'

class LoginAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginAttempt
        fields = '__all__'

