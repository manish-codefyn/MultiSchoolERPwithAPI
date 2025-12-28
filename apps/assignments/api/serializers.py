from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.api.serializers import TenantAwareSerializer, RelatedFieldAlternative
from apps.assignments.models import Assignment, Submission

# Import related models for Simple Serializers if needed, or use existing from other apps
# To be safe and self-contained or avoid circular imports, I often replicate Simple types.
from apps.students.models import Student
from apps.academics.models import AcademicYear, SchoolClass, Section, Subject

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

class SimpleSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'subject_type']

class SimpleAcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ['id', 'name', 'is_current']

# ============================================================================
# ASSIGNMENT SERIALIZERS
# ============================================================================

class AssignmentSerializer(TenantAwareSerializer):
    academic_year_detail = RelatedFieldAlternative(
        source='academic_year',
        read_only=True,
        serializer=SimpleAcademicYearSerializer
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
    subject_detail = RelatedFieldAlternative(
        source='subject',
        read_only=True,
        serializer=SimpleSubjectSerializer
    )
    teacher_detail = RelatedFieldAlternative(
        source='created_by_teacher',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    # Computed
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['id', 'is_overdue']

class SubmissionSerializer(TenantAwareSerializer):
    assignment_detail = RelatedFieldAlternative(
        source='assignment',
        read_only=True,
        serializer=AssignmentSerializer
    )
    student_detail = RelatedFieldAlternative(
        source='student',
        read_only=True,
        serializer=SimpleStudentSerializer
    )
    graded_by_detail = RelatedFieldAlternative(
        source='graded_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ['id', 'submitted_at', 'graded_at']

    def validate(self, attrs):
        # Additional custom validation if needed
        # (Model's clean method handles max_marks check, but we can do it here too)
        return super().validate(attrs)
