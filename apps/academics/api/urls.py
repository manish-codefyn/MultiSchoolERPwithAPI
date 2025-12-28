from django.urls import path
from .views import (
    AcademicYearListCreateAPIView, AcademicYearDetailAPIView,
    TermListCreateAPIView, TermDetailAPIView,
    SchoolClassListCreateAPIView, SchoolClassDetailAPIView,
    SectionListCreateAPIView, SectionDetailAPIView,
    HouseListCreateAPIView, HouseDetailAPIView,
    HousePointsListCreateAPIView, HousePointsDetailAPIView,
    SubjectListCreateAPIView, SubjectDetailAPIView,
    ClassSubjectListCreateAPIView, ClassSubjectDetailAPIView,
    TimeTableListCreateAPIView, TimeTableDetailAPIView,
    StudentAttendanceListCreateAPIView, StudentAttendanceDetailAPIView,
    HolidayListCreateAPIView, HolidayDetailAPIView,
    StudyMaterialListCreateAPIView, StudyMaterialDetailAPIView,
    SyllabusListCreateAPIView, SyllabusDetailAPIView,
    StreamListCreateAPIView, StreamDetailAPIView,
    ClassTeacherListCreateAPIView, ClassTeacherDetailAPIView,
    GradingSystemListCreateAPIView, GradingSystemDetailAPIView,
    GradeListCreateAPIView, GradeDetailAPIView
)

from .dashboard_view import AcademicsDashboardAPIView

urlpatterns = [
    # Dashboard
    path('dashboard/', AcademicsDashboardAPIView.as_view(), name='dashboard'),

    # Academic Year
    path('academic-years/', AcademicYearListCreateAPIView.as_view(), name='academic-year-list'),
    path('academic-years/<uuid:pk>/', AcademicYearDetailAPIView.as_view(), name='academic-year-detail'),

    # Term
    path('terms/', TermListCreateAPIView.as_view(), name='term-list'),
    path('terms/<uuid:pk>/', TermDetailAPIView.as_view(), name='term-detail'),

    # School Class
    path('classes/', SchoolClassListCreateAPIView.as_view(), name='school-class-list'),
    path('classes/<uuid:pk>/', SchoolClassDetailAPIView.as_view(), name='school-class-detail'),

    # Section
    path('sections/', SectionListCreateAPIView.as_view(), name='section-list'),
    path('sections/<uuid:pk>/', SectionDetailAPIView.as_view(), name='section-detail'),

    # Subject
    path('subjects/', SubjectListCreateAPIView.as_view(), name='subject-list'),
    path('subjects/<uuid:pk>/', SubjectDetailAPIView.as_view(), name='subject-detail'),

    # Class Subject
    path('class-subjects/', ClassSubjectListCreateAPIView.as_view(), name='class-subject-list'),
    path('class-subjects/<uuid:pk>/', ClassSubjectDetailAPIView.as_view(), name='class-subject-detail'),

    # Time Table
    path('timetables/', TimeTableListCreateAPIView.as_view(), name='timetable-list'),
    path('timetables/<uuid:pk>/', TimeTableDetailAPIView.as_view(), name='timetable-detail'),

    # Student Attendance
    path('attendance/', StudentAttendanceListCreateAPIView.as_view(), name='student-attendance-list'),
    path('attendance/<uuid:pk>/', StudentAttendanceDetailAPIView.as_view(), name='student-attendance-detail'),

    # Holiday
    path('holidays/', HolidayListCreateAPIView.as_view(), name='holiday-list'),
    path('holidays/<uuid:pk>/', HolidayDetailAPIView.as_view(), name='holiday-detail'),

    # Study Material
    path('study-materials/', StudyMaterialListCreateAPIView.as_view(), name='study-material-list'),
    path('study-materials/<uuid:pk>/', StudyMaterialDetailAPIView.as_view(), name='study-material-detail'),

    # Syllabus
    path('syllabus/', SyllabusListCreateAPIView.as_view(), name='syllabus-list'),
    path('syllabus/<uuid:pk>/', SyllabusDetailAPIView.as_view(), name='syllabus-detail'),

    # Stream
    path('streams/', StreamListCreateAPIView.as_view(), name='stream-list'),
    path('streams/<uuid:pk>/', StreamDetailAPIView.as_view(), name='stream-detail'),

    # Class Teacher
    path('class-teachers/', ClassTeacherListCreateAPIView.as_view(), name='class-teacher-list'),
    path('class-teachers/<uuid:pk>/', ClassTeacherDetailAPIView.as_view(), name='class-teacher-detail'),

    # Grading System
    path('grading-systems/', GradingSystemListCreateAPIView.as_view(), name='grading-system-list'),
    path('grading-systems/<uuid:pk>/', GradingSystemDetailAPIView.as_view(), name='grading-system-detail'),

    # Grade
    path('grades/', GradeListCreateAPIView.as_view(), name='grade-list'),
    path('grades/<uuid:pk>/', GradeDetailAPIView.as_view(), name='grade-detail'),

    # House
    path('houses/', HouseListCreateAPIView.as_view(), name='house-list'),
    path('houses/<uuid:pk>/', HouseDetailAPIView.as_view(), name='house-detail'),
    
    # House Points
    path('house-points/', HousePointsListCreateAPIView.as_view(), name='house-points-list'),
    path('house-points/<uuid:pk>/', HousePointsDetailAPIView.as_view(), name='house-points-detail'),
]
