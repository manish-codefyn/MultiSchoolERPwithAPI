from rest_framework import status
from rest_framework.response import Response
from apps.core.api.views import (
    BaseListCreateAPIView, BaseRetrieveUpdateDestroyAPIView
)
from apps.exams.models import (
    ExamType, Exam, ExamSubject, ExamResult, SubjectResult,
    MarkSheet, CompartmentExam, ResultStatistics
)
from apps.exams.api.serializers import (
    ExamTypeSerializer, ExamSerializer, ExamSubjectSerializer,
    ExamResultSerializer, SubjectResultSerializer, MarkSheetSerializer,
    CompartmentExamSerializer, ResultStatisticsSerializer
)

# ============================================================================
# EXAM TYPE VIEWS
# ============================================================================

class ExamTypeListCreateAPIView(BaseListCreateAPIView):
    model = ExamType
    serializer_class = ExamTypeSerializer
    search_fields = ['name', 'code']
    roles_required = ['admin', 'principal', 'teacher', 'student', 'parent']

class ExamTypeDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = ExamType
    serializer_class = ExamTypeSerializer
    roles_required = ['admin', 'principal', 'teacher']

# ============================================================================
# EXAM VIEWS
# ============================================================================

class ExamListCreateAPIView(BaseListCreateAPIView):
    model = Exam
    serializer_class = ExamSerializer
    search_fields = ['name', 'code']
    filterset_fields = ['exam_type', 'academic_year', 'class_name', 'status', 'is_published']
    roles_required = ['admin', 'principal', 'teacher', 'student', 'parent']

class ExamDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Exam
    serializer_class = ExamSerializer
    roles_required = ['admin', 'principal', 'teacher']

# ============================================================================
# EXAM SUBJECT VIEWS
# ============================================================================

class ExamSubjectListCreateAPIView(BaseListCreateAPIView):
    model = ExamSubject
    serializer_class = ExamSubjectSerializer
    filterset_fields = ['exam', 'subject', 'exam_date']
    roles_required = ['admin', 'principal', 'teacher', 'student', 'parent']

class ExamSubjectDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = ExamSubject
    serializer_class = ExamSubjectSerializer
    roles_required = ['admin', 'principal', 'teacher']

# ============================================================================
# EXAM RESULT VIEWS
# ============================================================================

class ExamResultListCreateAPIView(BaseListCreateAPIView):
    model = ExamResult
    serializer_class = ExamResultSerializer
    search_fields = ['student__first_name', 'student__admission_number']
    filterset_fields = ['exam', 'student', 'result_status', 'is_published', 'overall_grade']
    roles_required = ['admin', 'principal', 'teacher', 'student', 'parent']

class ExamResultDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = ExamResult
    serializer_class = ExamResultSerializer
    roles_required = ['admin', 'principal', 'teacher']

# ============================================================================
# SUBJECT RESULT VIEWS
# ============================================================================

class SubjectResultListCreateAPIView(BaseListCreateAPIView):
    model = SubjectResult
    serializer_class = SubjectResultSerializer
    filterset_fields = ['exam_result', 'exam_subject', 'is_pass']
    roles_required = ['admin', 'principal', 'teacher', 'student', 'parent']

class SubjectResultDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = SubjectResult
    serializer_class = SubjectResultSerializer
    roles_required = ['admin', 'principal', 'teacher']

# ============================================================================
# MARK SHEET VIEWS
# ============================================================================

class MarkSheetListCreateAPIView(BaseListCreateAPIView):
    model = MarkSheet
    serializer_class = MarkSheetSerializer
    search_fields = ['mark_sheet_number', 'verification_code']
    filterset_fields = ['exam_result', 'is_issued', 'is_verified']
    roles_required = ['admin', 'principal', 'teacher', 'student', 'parent']

class MarkSheetDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = MarkSheet
    serializer_class = MarkSheetSerializer
    roles_required = ['admin', 'principal', 'teacher']

# ============================================================================
# COMPARTMENT EXAM VIEWS
# ============================================================================

class CompartmentExamListCreateAPIView(BaseListCreateAPIView):
    model = CompartmentExam
    serializer_class = CompartmentExamSerializer
    filterset_fields = ['original_result', 'subject', 'status']
    roles_required = ['admin', 'principal', 'teacher', 'student', 'parent']

class CompartmentExamDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = CompartmentExam
    serializer_class = CompartmentExamSerializer
    roles_required = ['admin', 'principal', 'teacher']

# ============================================================================
# STATISTICS VIEWS
# ============================================================================

class ResultStatisticsListCreateAPIView(BaseListCreateAPIView):
    model = ResultStatistics
    serializer_class = ResultStatisticsSerializer
    filterset_fields = ['exam']
    roles_required = ['admin', 'principal', 'teacher']

class ResultStatisticsDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = ResultStatistics
    serializer_class = ResultStatisticsSerializer
    roles_required = ['admin', 'principal', 'teacher']
