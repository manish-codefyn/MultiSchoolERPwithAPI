from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.api.serializers import TenantAwareSerializer, RelatedFieldAlternative
from apps.exams.models import (
    ExamType, Exam, ExamSubject, ExamResult, SubjectResult,
    MarkSheet, CompartmentExam, ResultStatistics
)
from apps.academics.api.serializers import (
    AcademicYearSerializer, SchoolClassSerializer, SubjectSerializer,
    GradeSerializer
)

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

# ============================================================================
# EXAM CONFIGURATION SERIALIZERS
# ============================================================================

class ExamTypeSerializer(TenantAwareSerializer):
    class Meta:
        model = ExamType
        fields = '__all__'

class ExamSerializer(TenantAwareSerializer):
    exam_type_detail = RelatedFieldAlternative(
        source='exam_type',
        read_only=True,
        serializer=ExamTypeSerializer
    )
    academic_year_detail = RelatedFieldAlternative(
        source='academic_year',
        read_only=True,
        serializer=AcademicYearSerializer
    )
    class_name_detail = RelatedFieldAlternative(
        source='class_name',
        read_only=True,
        serializer=SchoolClassSerializer
    )
    
    # Computed fields
    duration_days = serializers.IntegerField(read_only=True)
    is_currently_running = serializers.BooleanField(read_only=True)

    class Meta:
        model = Exam
        fields = '__all__'
        read_only_fields = ['id', 'duration_days', 'is_currently_running']

class ExamSubjectSerializer(TenantAwareSerializer):
    exam_detail = RelatedFieldAlternative(
        source='exam',
        read_only=True,
        serializer=ExamSerializer
    )
    subject_detail = RelatedFieldAlternative(
        source='subject',
        read_only=True,
        serializer=SubjectSerializer
    )
    
    # Computed
    duration_hours = serializers.FloatField(read_only=True)

    class Meta:
        model = ExamSubject
        fields = '__all__'
        read_only_fields = ['id', 'duration_hours']

# ============================================================================
# RESULT SERIALIZERS
# ============================================================================

class ExamResultSerializer(TenantAwareSerializer):
    exam_detail = RelatedFieldAlternative(
        source='exam',
        read_only=True,
        serializer=ExamSerializer
    )
    overall_grade_detail = RelatedFieldAlternative(
        source='overall_grade',
        read_only=True,
        serializer=GradeSerializer
    )
    
    # Flattened Student Info
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_admission_number = serializers.CharField(source='student.admission_number', read_only=True)
    student_roll_number = serializers.CharField(source='student.roll_number', read_only=True)
    
    # Computed
    is_pass = serializers.BooleanField(read_only=True)
    percentage_display = serializers.CharField(read_only=True)

    class Meta:
        model = ExamResult
        fields = '__all__'
        read_only_fields = ['id', 'is_pass', 'percentage_display', 'rank', 'status']

class SubjectResultSerializer(TenantAwareSerializer):
    exam_result_detail = RelatedFieldAlternative(
        source='exam_result',
        read_only=True,
        serializer=ExamResultSerializer
    )
    exam_subject_detail = RelatedFieldAlternative(
        source='exam_subject',
        read_only=True,
        serializer=ExamSubjectSerializer
    )
    grade_detail = RelatedFieldAlternative(
        source='grade',
        read_only=True,
        serializer=GradeSerializer
    )
    
    # Computed
    percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = SubjectResult
        fields = '__all__'
        read_only_fields = ['id', 'percentage', 'grade_point']

class MarkSheetSerializer(TenantAwareSerializer):
    exam_result_detail = RelatedFieldAlternative(
        source='exam_result',
        read_only=True,
        serializer=ExamResultSerializer
    )
    issued_by_detail = RelatedFieldAlternative(
        source='issued_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    verified_by_detail = RelatedFieldAlternative(
        source='verified_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = MarkSheet
        fields = '__all__'
        read_only_fields = ['id', 'mark_sheet_number', 'verification_code', 'is_verified', 'verified_at']

class CompartmentExamSerializer(TenantAwareSerializer):
    original_result_detail = RelatedFieldAlternative(
        source='original_result',
        read_only=True,
        serializer=ExamResultSerializer
    )
    subject_detail = RelatedFieldAlternative(
        source='subject',
        read_only=True,
        serializer=SubjectSerializer
    )

    class Meta:
        model = CompartmentExam
        fields = '__all__'

class ResultStatisticsSerializer(TenantAwareSerializer):
    exam_detail = RelatedFieldAlternative(
        source='exam',
        read_only=True,
        serializer=ExamSerializer
    )

    class Meta:
        model = ResultStatistics
        fields = '__all__'
