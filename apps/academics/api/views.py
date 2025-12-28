from rest_framework import status
from apps.core.api.views import (
    BaseListCreateAPIView, BaseRetrieveUpdateDestroyAPIView
)
from apps.academics.models import (
    AcademicYear, Term, SchoolClass, Section, House, HousePoints,
    Subject, ClassSubject, TimeTable, StudentAttendance, Holiday,
    StudyMaterial, Syllabus, Stream, ClassTeacher, GradingSystem, Grade
)
from .serializers import (
    AcademicYearSerializer, TermSerializer, SchoolClassSerializer,
    SectionSerializer, HouseSerializer, HousePointsSerializer,
    SubjectSerializer, ClassSubjectSerializer, TimeTableSerializer,
    StudentAttendanceSerializer, HolidaySerializer, StudyMaterialSerializer,
    SyllabusSerializer, StreamSerializer, ClassTeacherSerializer,
    GradingSystemSerializer, GradeSerializer
)

# ============================================================================
# ACADEMIC YEAR
# ============================================================================

class AcademicYearListCreateAPIView(BaseListCreateAPIView):
    model = AcademicYear
    serializer_class = AcademicYearSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

class AcademicYearDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = AcademicYear
    serializer_class = AcademicYearSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

# ============================================================================
# TERM
# ============================================================================

class TermListCreateAPIView(BaseListCreateAPIView):
    model = Term
    serializer_class = TermSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

class TermDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Term
    serializer_class = TermSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

# ============================================================================
# SCHOOL CLASS
# ============================================================================

class SchoolClassListCreateAPIView(BaseListCreateAPIView):
    model = SchoolClass
    serializer_class = SchoolClassSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'TEACHER']

class SchoolClassDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = SchoolClass
    serializer_class = SchoolClassSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

# ============================================================================
# SECTION
# ============================================================================

class SectionListCreateAPIView(BaseListCreateAPIView):
    model = Section
    serializer_class = SectionSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'TEACHER']

class SectionDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Section
    serializer_class = SectionSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

# ============================================================================
# SUBJECT
# ============================================================================

class SubjectListCreateAPIView(BaseListCreateAPIView):
    model = Subject
    serializer_class = SubjectSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'TEACHER']

class SubjectDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Subject
    serializer_class = SubjectSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

# ============================================================================
# CLASS SUBJECT
# ============================================================================

class ClassSubjectListCreateAPIView(BaseListCreateAPIView):
    model = ClassSubject
    serializer_class = ClassSubjectSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'TEACHER']

class ClassSubjectDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = ClassSubject
    serializer_class = ClassSubjectSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

# ============================================================================
# TIME TABLE
# ============================================================================

class TimeTableListCreateAPIView(BaseListCreateAPIView):
    model = TimeTable
    serializer_class = TimeTableSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'TEACHER', 'STUDENT']

class TimeTableDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = TimeTable
    serializer_class = TimeTableSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'TEACHER']

# ============================================================================
# STUDENT ATTENDANCE
# ============================================================================

class StudentAttendanceListCreateAPIView(BaseListCreateAPIView):
    model = StudentAttendance
    serializer_class = StudentAttendanceSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'TEACHER', 'STUDENT']

class StudentAttendanceDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = StudentAttendance
    serializer_class = StudentAttendanceSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'TEACHER']

# ============================================================================
# HOLIDAY
# ============================================================================

class HolidayListCreateAPIView(BaseListCreateAPIView):
    model = Holiday
    serializer_class = HolidaySerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'TEACHER', 'STUDENT']

class HolidayDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Holiday
    serializer_class = HolidaySerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

# ============================================================================
# STUDY MATERIAL
# ============================================================================

class StudyMaterialListCreateAPIView(BaseListCreateAPIView):
    model = StudyMaterial
    serializer_class = StudyMaterialSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'TEACHER', 'STUDENT']

class StudyMaterialDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = StudyMaterial
    serializer_class = StudyMaterialSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'TEACHER']

# ============================================================================
# SYLLABUS
# ============================================================================

class SyllabusListCreateAPIView(BaseListCreateAPIView):
    model = Syllabus
    serializer_class = SyllabusSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'TEACHER', 'STUDENT']

class SyllabusDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Syllabus
    serializer_class = SyllabusSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'TEACHER']

# ============================================================================
# STREAM
# ============================================================================

class StreamListCreateAPIView(BaseListCreateAPIView):
    model = Stream
    serializer_class = StreamSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

class StreamDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Stream
    serializer_class = StreamSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

# ============================================================================
# CLASS TEACHER
# ============================================================================

class ClassTeacherListCreateAPIView(BaseListCreateAPIView):
    model = ClassTeacher
    serializer_class = ClassTeacherSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

class ClassTeacherDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = ClassTeacher
    serializer_class = ClassTeacherSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

# ============================================================================
# GRADING SYSTEM
# ============================================================================

class GradingSystemListCreateAPIView(BaseListCreateAPIView):
    model = GradingSystem
    serializer_class = GradingSystemSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

class GradingSystemDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = GradingSystem
    serializer_class = GradingSystemSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

# ============================================================================
# GRADE
# ============================================================================

class GradeListCreateAPIView(BaseListCreateAPIView):
    model = Grade
    serializer_class = GradeSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

class GradeDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Grade
    serializer_class = GradeSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

# ============================================================================
# HOUSE
# ============================================================================

class HouseListCreateAPIView(BaseListCreateAPIView):
    model = House
    serializer_class = HouseSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'TEACHER']

class HouseDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = House
    serializer_class = HouseSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']

class HousePointsListCreateAPIView(BaseListCreateAPIView):
    model = HousePoints
    serializer_class = HousePointsSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'TEACHER']

class HousePointsDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = HousePoints
    serializer_class = HousePointsSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'TEACHER']
