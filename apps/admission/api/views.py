from rest_framework import status
from rest_framework.response import Response
from apps.core.api.views import (
    BaseListCreateAPIView, BaseRetrieveUpdateDestroyAPIView
)
from apps.admission.models import (
    AdmissionCycle, AdmissionProgram, OnlineApplication, ApplicationDocument
)
from apps.admission.api.serializers import (
    AdmissionCycleSerializer, AdmissionProgramSerializer,
    OnlineApplicationSerializer, ApplicationDocumentSerializer
)

# ============================================================================
# CYCLE & PROGRAM VIEWS
# ============================================================================

class AdmissionCycleListCreateAPIView(BaseListCreateAPIView):
    model = AdmissionCycle
    serializer_class = AdmissionCycleSerializer
    search_fields = ['name', 'code', 'academic_year__name']
    filterset_fields = ['status', 'school_level', 'academic_year', 'is_active']
    roles_required = ['admin', 'admissions_officer']

class AdmissionCycleDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = AdmissionCycle
    serializer_class = AdmissionCycleSerializer
    roles_required = ['admin', 'admissions_officer']


class AdmissionProgramListCreateAPIView(BaseListCreateAPIView):
    model = AdmissionProgram
    serializer_class = AdmissionProgramSerializer
    search_fields = ['program_name', 'class_grade']
    filterset_fields = ['admission_cycle', 'program_type', 'stream', 'is_active']
    roles_required = ['admin', 'admissions_officer']

class AdmissionProgramDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = AdmissionProgram
    serializer_class = AdmissionProgramSerializer
    roles_required = ['admin', 'admissions_officer']

# ============================================================================
# APPLICATION VIEWS
# ============================================================================

class OnlineApplicationListCreateAPIView(BaseListCreateAPIView):
    model = OnlineApplication
    serializer_class = OnlineApplicationSerializer
    search_fields = ['application_number', 'first_name', 'email', 'phone']
    filterset_fields = ['admission_cycle', 'program', 'status', 'gender', 'category']
    roles_required = ['admin', 'admissions_officer', 'parent']

class OnlineApplicationDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = OnlineApplication
    serializer_class = OnlineApplicationSerializer
    roles_required = ['admin', 'admissions_officer', 'parent']


class ApplicationDocumentListCreateAPIView(BaseListCreateAPIView):
    model = ApplicationDocument
    serializer_class = ApplicationDocumentSerializer
    search_fields = ['file_name', 'description']
    filterset_fields = ['application', 'document_type', 'is_verified']
    roles_required = ['admin', 'admissions_officer', 'parent']

class ApplicationDocumentDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = ApplicationDocument
    serializer_class = ApplicationDocumentSerializer
    roles_required = ['admin', 'admissions_officer']
