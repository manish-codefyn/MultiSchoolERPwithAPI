from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.api.serializers import TenantAwareSerializer, RelatedFieldAlternative
from apps.academics.models import StudentAttendance, SchoolClass, Section
from apps.hr.models import StaffAttendance
from apps.hostel.models import HostelAttendance, Hostel
from apps.transportation.models import TransportAttendance, Route
from apps.students.models import Student

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

class SimpleSchoolClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolClass
        fields = ['id', 'name', 'code']

class SimpleSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'name']

# ============================================================================
# STUDENT ATTENDANCE SERIALIZERS
# ============================================================================

class StudentAttendanceSerializer(TenantAwareSerializer):
    student_detail = RelatedFieldAlternative(
        source='student',
        read_only=True,
        serializer=SimpleStudentSerializer
    )
    class_detail = RelatedFieldAlternative(
        source='class_name',
        read_only=True,
        serializer=SimpleSchoolClassSerializer
    )
    section_detail = RelatedFieldAlternative(
        source='section',
        read_only=True,
        serializer=SimpleSectionSerializer
    )
    marked_by_detail = RelatedFieldAlternative(
        source='marked_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = StudentAttendance
        fields = '__all__'

# ============================================================================
# STAFF ATTENDANCE SERIALIZERS
# ============================================================================

class StaffAttendanceSerializer(TenantAwareSerializer):
    marked_by_detail = RelatedFieldAlternative(
        source='marked_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = StaffAttendance
        fields = '__all__'

# ============================================================================
# HOSTEL ATTENDANCE SERIALIZERS
# ============================================================================

class HostelAttendanceSerializer(TenantAwareSerializer):
    student_detail = RelatedFieldAlternative(
        source='student',
        read_only=True,
        serializer=SimpleStudentSerializer
    )
    marked_by_detail = RelatedFieldAlternative(
        source='marked_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = HostelAttendance
        fields = '__all__'

# ============================================================================
# TRANSPORT ATTENDANCE SERIALIZERS
# ============================================================================

class TransportAttendanceSerializer(TenantAwareSerializer):
    student_detail = RelatedFieldAlternative(
        source='student',
        read_only=True,
        serializer=SimpleStudentSerializer
    )
    marked_by_detail = RelatedFieldAlternative(
        source='marked_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = TransportAttendance
        fields = '__all__'
