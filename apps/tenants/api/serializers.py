from rest_framework import serializers
from apps.tenants.models import *

class TenantSerializer(serializers.ModelSerializer):
    branding_info = serializers.ReadOnlyField()

    class Meta:
        model = Tenant
        fields = '__all__'

class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = '__all__'

class TenantConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantConfiguration
        fields = '__all__'

class PaymentConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentConfiguration
        fields = '__all__'

class AnalyticsConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsConfiguration
        fields = '__all__'

class SystemNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemNotification
        fields = '__all__'

class APIServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIServiceCategory
        fields = '__all__'

class APIServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIService
        fields = '__all__'

class TenantAPIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantAPIKey
        fields = '__all__'

class APIUsageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIUsageLog
        fields = '__all__'

class TenantSecretSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantSecret
        fields = '__all__'

class VideoAPIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoAPIKey
        fields = '__all__'

class WhatsAppAPIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppAPIKey
        fields = '__all__'

class SMSAPIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSAPIKey
        fields = '__all__'

class AIAPIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAPIKey
        fields = '__all__'

