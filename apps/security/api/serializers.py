from rest_framework import serializers
from apps.security.models import *

class SecurityPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityPolicy
        fields = '__all__'

class PasswordPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordPolicy
        fields = '__all__'

class SessionPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionPolicy
        fields = '__all__'

class AccessControlPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessControlPolicy
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'
        ref_name = "SecurityAuditLog"

class SecurityIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityIncident
        fields = '__all__'

class IncidentTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentTimeline
        fields = '__all__'

class ThreatIntelligenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreatIntelligence
        fields = '__all__'

class SecurityScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityScan
        fields = '__all__'

