from django.urls import path
from apps.admission.api.views import (
    AdmissionCycleListCreateAPIView, AdmissionCycleDetailAPIView,
    AdmissionProgramListCreateAPIView, AdmissionProgramDetailAPIView,
    OnlineApplicationListCreateAPIView, OnlineApplicationDetailAPIView,
    ApplicationDocumentListCreateAPIView, ApplicationDocumentDetailAPIView
)

urlpatterns = [
    # Cycles
    path('cycles/', AdmissionCycleListCreateAPIView.as_view(), name='admissioncycle-list'),
    path('cycles/<uuid:pk>/', AdmissionCycleDetailAPIView.as_view(), name='admissioncycle-detail'),

    # Programs
    path('programs/', AdmissionProgramListCreateAPIView.as_view(), name='admissionprogram-list'),
    path('programs/<uuid:pk>/', AdmissionProgramDetailAPIView.as_view(), name='admissionprogram-detail'),

    # Applications
    path('applications/', OnlineApplicationListCreateAPIView.as_view(), name='onlineapplication-list'),
    path('applications/<uuid:pk>/', OnlineApplicationDetailAPIView.as_view(), name='onlineapplication-detail'),

    # Documents
    path('documents/', ApplicationDocumentListCreateAPIView.as_view(), name='applicationdocument-list'),
    path('documents/<uuid:pk>/', ApplicationDocumentDetailAPIView.as_view(), name='applicationdocument-detail'),
]
