from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.api.serializers import TenantAwareSerializer, RelatedFieldAlternative
from apps.events.models import (
    EventCategory, Event, EventRegistration, EventDocument,
    EventTask, EventExpense, EventGallery, GalleryImage,
    EventFeedback, RecurringEventPattern
)
# Importing Student/Academics models for Simple serializers or standard references
from apps.students.models import Student
from apps.academics.models import AcademicYear, SchoolClass, Section

User = get_user_model()

# ============================================================================
# HELPER SERIALIZERS
# ============================================================================

class SimpleUserSerializer(serializers.ModelSerializer):
    """Simple serializer for user details"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role']

class SimpleStudentSerializer(serializers.ModelSerializer):
    """Simple serializer for student details"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'admission_number', 'full_name', 'current_class_name']

class SimpleAcademicYearSerializer(serializers.ModelSerializer):
    """Simple serializer for academic year"""
    class Meta:
        model = AcademicYear
        fields = ['id', 'name', 'start_date', 'end_date', 'is_current']

# ============================================================================
# EVENT CONFIG SERIALIZERS
# ============================================================================

class EventCategorySerializer(TenantAwareSerializer):
    class Meta:
        model = EventCategory
        fields = '__all__'

# ============================================================================
# EVENT CORE SERIALIZERS
# ============================================================================

class EventSerializer(TenantAwareSerializer):
    category_detail = RelatedFieldAlternative(
        source='category',
        read_only=True,
        serializer=EventCategorySerializer
    )
    academic_year_detail = RelatedFieldAlternative(
        source='academic_year',
        read_only=True,
        serializer=SimpleAcademicYearSerializer
    )
    
    # M2M Relationships (Just names or IDs for simplicity, or define Nested if needed)
    target_classes_names = serializers.StringRelatedField(source='target_classes', many=True, read_only=True)
    target_sections_names = serializers.StringRelatedField(source='target_sections', many=True, read_only=True)

    # Computed Properties
    duration_days = serializers.IntegerField(read_only=True)
    is_current = serializers.BooleanField(read_only=True)
    days_until_event = serializers.IntegerField(read_only=True)
    registration_count = serializers.IntegerField(read_only=True)
    is_registration_open = serializers.BooleanField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    available_slots = serializers.IntegerField(read_only=True)
    tag_list = serializers.ListField(read_only=True)

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = [
            'id', 'duration_days', 'is_current', 'days_until_event',
            'registration_count', 'is_registration_open', 'is_full',
            'available_slots', 'tag_list'
        ]

class EventRegistrationSerializer(TenantAwareSerializer):
    event_detail = RelatedFieldAlternative(
        source='event',
        read_only=True,
        serializer=EventSerializer
    )
    student_detail = RelatedFieldAlternative(
        source='student',
        read_only=True,
        serializer=SimpleStudentSerializer
    )
    user_detail = RelatedFieldAlternative(
        source='user',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    
    registrant_name = serializers.CharField(source='get_registrant_name', read_only=True)
    registrant_email = serializers.CharField(source='get_registrant_email', read_only=True)

    class Meta:
        model = EventRegistration
        fields = '__all__'
        read_only_fields = ['id', 'registrant_name', 'registrant_email']

class EventDocumentSerializer(TenantAwareSerializer):
    event_detail = RelatedFieldAlternative(
        source='event',
        read_only=True,
        serializer=EventSerializer
    )
    uploaded_by_detail = RelatedFieldAlternative(
        source='uploaded_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = EventDocument
        fields = '__all__'

# ============================================================================
# EVENT MANAGEMENT SERIALIZERS
# ============================================================================

class EventTaskSerializer(TenantAwareSerializer):
    event_detail = RelatedFieldAlternative(
        source='event',
        read_only=True,
        serializer=EventSerializer
    )
    assigned_to_detail = RelatedFieldAlternative(
        source='assigned_to',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    
    # Computed
    is_overdue = serializers.BooleanField(read_only=True)
    progress_percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = EventTask
        fields = '__all__'
        read_only_fields = ['id', 'is_overdue', 'progress_percentage']

class EventExpenseSerializer(TenantAwareSerializer):
    event_detail = RelatedFieldAlternative(
        source='event',
        read_only=True,
        serializer=EventSerializer
    )
    
    # Computed
    balance_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_fully_paid = serializers.BooleanField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = EventExpense
        fields = '__all__'
        read_only_fields = ['id', 'balance_due', 'is_fully_paid', 'is_overdue']

# ============================================================================
# EVENT MEDIA & FEEDBACK SERIALIZERS
# ============================================================================

class EventGallerySerializer(TenantAwareSerializer):
    event_detail = RelatedFieldAlternative(
        source='event',
        read_only=True,
        serializer=EventSerializer
    )

    class Meta:
        model = EventGallery
        fields = '__all__'

class GalleryImageSerializer(TenantAwareSerializer):
    gallery_detail = RelatedFieldAlternative(
        source='gallery',
        read_only=True,
        serializer=EventGallerySerializer
    )
    uploaded_by_detail = RelatedFieldAlternative(
        source='uploaded_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = GalleryImage
        fields = '__all__'

class EventFeedbackSerializer(TenantAwareSerializer):
    event_detail = RelatedFieldAlternative(
        source='event',
        read_only=True,
        serializer=EventSerializer
    )
    registration_detail = RelatedFieldAlternative(
        source='registration',
        read_only=True,
        serializer=EventRegistrationSerializer
    )
    
    # Computed
    average_rating = serializers.FloatField(read_only=True)
    attendee_name = serializers.CharField(read_only=True)

    class Meta:
        model = EventFeedback
        fields = '__all__'
        read_only_fields = ['id', 'average_rating', 'attendee_name']

class RecurringEventPatternSerializer(TenantAwareSerializer):
    base_event_detail = RelatedFieldAlternative(
        source='base_event',
        read_only=True,
        serializer=EventSerializer
    )
    
    weekdays_list = serializers.ListField(source='get_weekdays_list', read_only=True)

    class Meta:
        model = RecurringEventPattern
        fields = '__all__'
        read_only_fields = ['id', 'weekdays_list']
