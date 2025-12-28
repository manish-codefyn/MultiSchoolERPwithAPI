from rest_framework import serializers
from apps.core.models import AuditLog

class BaseModelSerializer(serializers.ModelSerializer):
    """
    Base serializer for all application models
    """
    pass

class TenantAwareSerializer(BaseModelSerializer):
    """
    Serializer that automatically handles tenant filtering and assignment
    """
    
    def create(self, validated_data):
        """
        Ensure tenant is added to validated data from context
        """
        request = self.context.get('request')
        if request and hasattr(request, 'tenant') and request.tenant:
            # Check if model has tenant field
            if hasattr(self.Meta.model, 'tenant'):
                validated_data['tenant'] = request.tenant
                
        return super().create(validated_data)

class AuditLogSerializer(BaseModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'
        ref_name = "CoreAuditLog"

class RelatedFieldAlternative(serializers.PrimaryKeyRelatedField):
    """
    Serializer field that returns PK by default but full object on request.
    Useful for getting nested details (e.g. key_detail) while writing with key_id.
    """
    
    def __init__(self, **kwargs):
        self.serializer = kwargs.pop('serializer', None)
        super().__init__(**kwargs)
    
    def use_pk_only_optimization(self):
        return not self.serializer
    
    def to_representation(self, instance):
        if self.serializer:
            return self.serializer(instance, context=self.context).data
        return super().to_representation(instance)
