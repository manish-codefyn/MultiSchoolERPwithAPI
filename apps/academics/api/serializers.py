from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.api.serializers import TenantAwareSerializer, RelatedFieldAlternative
from apps.academics.models import (
    AcademicYear, Term, SchoolClass, Section, House, HousePoints,
    Subject, ClassSubject, TimeTable, StudentAttendance, Holiday,
    StudyMaterial, Syllabus, Stream, ClassTeacher, GradingSystem, Grade
)

User = get_user_model()

# ============================================================================
# HELPER SERIALIZERS
# ============================================================================

class SimpleUserSerializer(serializers.ModelSerializer):
    """Simple serializer for user details (teachers, staff)"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role']

# ============================================================================
# ACADEMIC YEAR & TERM
# ============================================================================

class AcademicYearSerializer(TenantAwareSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'

class TermSerializer(TenantAwareSerializer):
    academic_year_detail = RelatedFieldAlternative(
        source='academic_year',
        read_only=True,
        serializer=AcademicYearSerializer
    )

    class Meta:
        model = Term
        fields = '__all__'

# ============================================================================
# SCHOOL CLASS & SECTION
# ============================================================================

class SchoolClassSerializer(TenantAwareSerializer):
    class_teacher_detail = RelatedFieldAlternative(
        source='class_teacher',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    current_strength = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)

    class Meta:
        model = SchoolClass
        fields = '__all__'
        read_only_fields = ['id', 'current_strength', 'available_seats']

class SectionSerializer(TenantAwareSerializer):
    class_name_detail = RelatedFieldAlternative(
        source='class_name',
        read_only=True,
        serializer=SchoolClassSerializer
    )
    section_incharge_detail = RelatedFieldAlternative(
        source='section_incharge',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    current_strength = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Section
        fields = '__all__'
        read_only_fields = ['id', 'current_strength']

# ============================================================================
# SUBJECTS & TEACHING
# ============================================================================

class SubjectSerializer(TenantAwareSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class ClassSubjectSerializer(TenantAwareSerializer):
    class_name_detail = RelatedFieldAlternative(
        source='class_name',
        read_only=True,
        serializer=SchoolClassSerializer
    )
    subject_detail = RelatedFieldAlternative(
        source='subject',
        read_only=True,
        serializer=SubjectSerializer
    )
    teacher_detail = RelatedFieldAlternative(
        source='teacher',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    academic_year_detail = RelatedFieldAlternative(
        source='academic_year',
        read_only=True,
        serializer=AcademicYearSerializer
    )

    class Meta:
        model = ClassSubject
        fields = '__all__'

# ============================================================================
# TIMETABLE
# ============================================================================

class TimeTableSerializer(TenantAwareSerializer):
    class_name_detail = RelatedFieldAlternative(
        source='class_name',
        read_only=True,
        serializer=SchoolClassSerializer
    )
    section_detail = RelatedFieldAlternative(
        source='section',
        read_only=True,
        serializer=SectionSerializer
    )
    subject_detail = RelatedFieldAlternative(
        source='subject',
        read_only=True,
        serializer=ClassSubjectSerializer
    )
    teacher_detail = RelatedFieldAlternative(
        source='teacher',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = TimeTable
        fields = '__all__'

# ============================================================================
# HOUSE
# ============================================================================

class HouseSerializer(TenantAwareSerializer):
    house_master_detail = RelatedFieldAlternative(
        source='house_master',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = House
        fields = '__all__'

class HousePointsSerializer(TenantAwareSerializer):
    house_detail = RelatedFieldAlternative(
        source='house',
        read_only=True,
        serializer=HouseSerializer
    )
    awarded_by_detail = RelatedFieldAlternative(
        source='awarded_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = HousePoints
        fields = '__all__'

# ============================================================================
# ATTENDANCE
# ============================================================================

class StudentAttendanceSerializer(TenantAwareSerializer):
    # Need to handle Student serialization carefully to avoid circular imports?
    # Ideally should import StudentSerializer but that's in apps.students. Also circular?
    # For now, just basic details or a minimal local Student definition.
    # But StudentAttendance in 'students' app usually handles this? 
    # Wait, StudentAttendance is in 'academics'. 
    
    class_name_detail = RelatedFieldAlternative(
        source='class_name',
        read_only=True,
        serializer=SchoolClassSerializer
    )
    section_detail = RelatedFieldAlternative(
        source='section',
        read_only=True,
        serializer=SectionSerializer
    )
    marked_by_detail = RelatedFieldAlternative(
        source='marked_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    # Basic student info check
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = StudentAttendance
        fields = '__all__'

# ============================================================================
# OTHER ACADEMICS
# ============================================================================

class HolidaySerializer(TenantAwareSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'
        ref_name = "AcademicsHoliday"

class StudyMaterialSerializer(TenantAwareSerializer):
    uploaded_by_detail = RelatedFieldAlternative(
        source='uploaded_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    class_name_detail = RelatedFieldAlternative(
        source='class_name',
        read_only=True,
        serializer=SchoolClassSerializer
    )
    subject_detail = RelatedFieldAlternative(
        source='subject',
        read_only=True,
        serializer=SubjectSerializer
    )

    class Meta:
        model = StudyMaterial
        fields = '__all__'

class SyllabusSerializer(TenantAwareSerializer):
    class_name_detail = RelatedFieldAlternative(
        source='class_name',
        read_only=True,
        serializer=SchoolClassSerializer
    )
    subject_detail = RelatedFieldAlternative(
        source='subject',
        read_only=True,
        serializer=SubjectSerializer
    )

    class Meta:
        model = Syllabus
        fields = '__all__'

class StreamSerializer(TenantAwareSerializer):
    class Meta:
        model = Stream
        fields = '__all__'

class ClassTeacherSerializer(TenantAwareSerializer):
    teacher_detail = RelatedFieldAlternative(
        source='teacher',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    class_name_detail = RelatedFieldAlternative(
        source='class_name',
        read_only=True,
        serializer=SchoolClassSerializer
    )

    class Meta:
        model = ClassTeacher
        fields = '__all__'

class GradingSystemSerializer(TenantAwareSerializer):
    class Meta:
        model = GradingSystem
        fields = '__all__'

class GradeSerializer(TenantAwareSerializer):
    grading_system_detail = RelatedFieldAlternative(
        source='grading_system',
        read_only=True,
        serializer=GradingSystemSerializer
    )

    class Meta:
        model = Grade
        fields = '__all__'
