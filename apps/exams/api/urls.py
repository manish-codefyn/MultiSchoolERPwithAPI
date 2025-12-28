from django.urls import path
from apps.exams.api.views import (
    ExamTypeListCreateAPIView, ExamTypeDetailAPIView,
    ExamListCreateAPIView, ExamDetailAPIView,
    ExamSubjectListCreateAPIView, ExamSubjectDetailAPIView,
    ExamResultListCreateAPIView, ExamResultDetailAPIView,
    SubjectResultListCreateAPIView, SubjectResultDetailAPIView,
    MarkSheetListCreateAPIView, MarkSheetDetailAPIView,
    CompartmentExamListCreateAPIView, CompartmentExamDetailAPIView,
    CompartmentExamListCreateAPIView, CompartmentExamDetailAPIView,
    ResultStatisticsListCreateAPIView, ResultStatisticsDetailAPIView
)
from .dashboard_view import ExamsDashboardAPIView


urlpatterns = [
    # Dashboard
    path('dashboard/', ExamsDashboardAPIView.as_view(), name='dashboard'),

    # Exam Types
    path('types/', ExamTypeListCreateAPIView.as_view(), name='examtype-list'),
    path('types/<uuid:pk>/', ExamTypeDetailAPIView.as_view(), name='examtype-detail'),

    # Exams
    path('', ExamListCreateAPIView.as_view(), name='exam-list'),
    path('<uuid:pk>/', ExamDetailAPIView.as_view(), name='exam-detail'),

    # Exam Subjects
    path('subjects/', ExamSubjectListCreateAPIView.as_view(), name='examsubject-list'),
    path('subjects/<uuid:pk>/', ExamSubjectDetailAPIView.as_view(), name='examsubject-detail'),

    # Results
    path('results/', ExamResultListCreateAPIView.as_view(), name='examresult-list'),
    path('results/<uuid:pk>/', ExamResultDetailAPIView.as_view(), name='examresult-detail'),

    # Subject Results
    path('subject-results/', SubjectResultListCreateAPIView.as_view(), name='subjectresult-list'),
    path('subject-results/<uuid:pk>/', SubjectResultDetailAPIView.as_view(), name='subjectresult-detail'),

    # Mark Sheets
    path('marksheets/', MarkSheetListCreateAPIView.as_view(), name='marksheet-list'),
    path('marksheets/<uuid:pk>/', MarkSheetDetailAPIView.as_view(), name='marksheet-detail'),

    # Compartment Exams
    path('compartment/', CompartmentExamListCreateAPIView.as_view(), name='compartmentexam-list'),
    path('compartment/<uuid:pk>/', CompartmentExamDetailAPIView.as_view(), name='compartmentexam-detail'),

    # Statistics
    path('statistics/', ResultStatisticsListCreateAPIView.as_view(), name='resultstatistics-list'),
    path('statistics/<uuid:pk>/', ResultStatisticsDetailAPIView.as_view(), name='resultstatistics-detail'),
]
