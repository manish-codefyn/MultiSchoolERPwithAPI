from rest_framework import status
from apps.core.api.views import (
    BaseListCreateAPIView, BaseRetrieveUpdateDestroyAPIView
)
from apps.hr.models import (
    Department, Qualification, Designation, Staff, StaffAddress, StaffDocument,
    StaffAttendance, LeaveType, LeaveApplication, LeaveBalance, SalaryStructure,
    Payroll, Promotion, EmploymentHistory, TrainingProgram, TrainingParticipation,
    PerformanceReview, Recruitment, JobApplication, Holiday, WorkSchedule,
    TaxConfig, PFESIConfig, DisciplinaryAction, Asset, AssetAssignment
)
from .serializers import (
    DepartmentSerializer, QualificationSerializer, DesignationSerializer,
    StaffSerializer, StaffAddressSerializer, StaffDocumentSerializer,
    StaffAttendanceSerializer, LeaveTypeSerializer, LeaveApplicationSerializer,
    LeaveBalanceSerializer, SalaryStructureSerializer, PayrollSerializer,
    PromotionSerializer, EmploymentHistorySerializer, TrainingProgramSerializer,
    TrainingParticipationSerializer, PerformanceReviewSerializer,
    RecruitmentSerializer, JobApplicationSerializer, HolidaySerializer,
    WorkScheduleSerializer, TaxConfigSerializer, PFESIConfigSerializer,
    DisciplinaryActionSerializer, AssetSerializer, AssetAssignmentSerializer
)

# Department
class DepartmentListCreateAPIView(BaseListCreateAPIView):
    model = Department
    serializer_class = DepartmentSerializer
    roles_required = ['HR', 'ADMIN']

class DepartmentDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Department
    serializer_class = DepartmentSerializer
    roles_required = ['HR', 'ADMIN']

# Qualification
class QualificationListCreateAPIView(BaseListCreateAPIView):
    model = Qualification
    serializer_class = QualificationSerializer
    roles_required = ['HR', 'ADMIN']

class QualificationDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Qualification
    serializer_class = QualificationSerializer
    roles_required = ['HR', 'ADMIN']

# Designation
class DesignationListCreateAPIView(BaseListCreateAPIView):
    model = Designation
    serializer_class = DesignationSerializer
    roles_required = ['HR', 'ADMIN']

class DesignationDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Designation
    serializer_class = DesignationSerializer
    roles_required = ['HR', 'ADMIN']

# Staff
class StaffListCreateAPIView(BaseListCreateAPIView):
    model = Staff
    serializer_class = StaffSerializer
    roles_required = ['HR', 'ADMIN']

class StaffDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Staff
    serializer_class = StaffSerializer
    roles_required = ['HR', 'ADMIN']

# StaffAddress
class StaffAddressListCreateAPIView(BaseListCreateAPIView):
    model = StaffAddress
    serializer_class = StaffAddressSerializer
    roles_required = ['HR', 'ADMIN']

class StaffAddressDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = StaffAddress
    serializer_class = StaffAddressSerializer
    roles_required = ['HR', 'ADMIN']

# StaffDocument
class StaffDocumentListCreateAPIView(BaseListCreateAPIView):
    model = StaffDocument
    serializer_class = StaffDocumentSerializer
    roles_required = ['HR', 'ADMIN']

class StaffDocumentDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = StaffDocument
    serializer_class = StaffDocumentSerializer
    roles_required = ['HR', 'ADMIN']

# StaffAttendance
class StaffAttendanceListCreateAPIView(BaseListCreateAPIView):
    model = StaffAttendance
    serializer_class = StaffAttendanceSerializer
    roles_required = ['HR', 'ADMIN', 'TEACHER', 'STAFF']

class StaffAttendanceDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = StaffAttendance
    serializer_class = StaffAttendanceSerializer
    roles_required = ['HR', 'ADMIN', 'TEACHER', 'STAFF']

# LeaveType
class LeaveTypeListCreateAPIView(BaseListCreateAPIView):
    model = LeaveType
    serializer_class = LeaveTypeSerializer
    roles_required = ['HR', 'ADMIN']

class LeaveTypeDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = LeaveType
    serializer_class = LeaveTypeSerializer
    roles_required = ['HR', 'ADMIN']

# LeaveApplication
class LeaveApplicationListCreateAPIView(BaseListCreateAPIView):
    model = LeaveApplication
    serializer_class = LeaveApplicationSerializer
    roles_required = ['HR', 'ADMIN', 'TEACHER', 'STAFF']

class LeaveApplicationDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = LeaveApplication
    serializer_class = LeaveApplicationSerializer
    roles_required = ['HR', 'ADMIN', 'TEACHER', 'STAFF']

# LeaveBalance
class LeaveBalanceListCreateAPIView(BaseListCreateAPIView):
    model = LeaveBalance
    serializer_class = LeaveBalanceSerializer
    roles_required = ['HR', 'ADMIN']

class LeaveBalanceDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = LeaveBalance
    serializer_class = LeaveBalanceSerializer
    roles_required = ['HR', 'ADMIN']

# SalaryStructure
class SalaryStructureListCreateAPIView(BaseListCreateAPIView):
    model = SalaryStructure
    serializer_class = SalaryStructureSerializer
    roles_required = ['HR', 'ADMIN', 'ACCOUNTANT']

class SalaryStructureDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = SalaryStructure
    serializer_class = SalaryStructureSerializer
    roles_required = ['HR', 'ADMIN', 'ACCOUNTANT']

# Payroll
class PayrollListCreateAPIView(BaseListCreateAPIView):
    model = Payroll
    serializer_class = PayrollSerializer
    roles_required = ['HR', 'ADMIN', 'ACCOUNTANT']

class PayrollDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Payroll
    serializer_class = PayrollSerializer
    roles_required = ['HR', 'ADMIN', 'ACCOUNTANT']

# Promotion
class PromotionListCreateAPIView(BaseListCreateAPIView):
    model = Promotion
    serializer_class = PromotionSerializer
    roles_required = ['HR', 'ADMIN']

class PromotionDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Promotion
    serializer_class = PromotionSerializer
    roles_required = ['HR', 'ADMIN']

# EmploymentHistory
class EmploymentHistoryListCreateAPIView(BaseListCreateAPIView):
    model = EmploymentHistory
    serializer_class = EmploymentHistorySerializer
    roles_required = ['HR', 'ADMIN']

class EmploymentHistoryDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = EmploymentHistory
    serializer_class = EmploymentHistorySerializer
    roles_required = ['HR', 'ADMIN']

# TrainingProgram
class TrainingProgramListCreateAPIView(BaseListCreateAPIView):
    model = TrainingProgram
    serializer_class = TrainingProgramSerializer
    roles_required = ['HR', 'ADMIN']

class TrainingProgramDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = TrainingProgram
    serializer_class = TrainingProgramSerializer
    roles_required = ['HR', 'ADMIN']

# TrainingParticipation
class TrainingParticipationListCreateAPIView(BaseListCreateAPIView):
    model = TrainingParticipation
    serializer_class = TrainingParticipationSerializer
    roles_required = ['HR', 'ADMIN']

class TrainingParticipationDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = TrainingParticipation
    serializer_class = TrainingParticipationSerializer
    roles_required = ['HR', 'ADMIN']

# PerformanceReview
class PerformanceReviewListCreateAPIView(BaseListCreateAPIView):
    model = PerformanceReview
    serializer_class = PerformanceReviewSerializer
    roles_required = ['HR', 'ADMIN']

class PerformanceReviewDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = PerformanceReview
    serializer_class = PerformanceReviewSerializer
    roles_required = ['HR', 'ADMIN']

# Recruitment
class RecruitmentListCreateAPIView(BaseListCreateAPIView):
    model = Recruitment
    serializer_class = RecruitmentSerializer
    roles_required = ['HR', 'ADMIN']

class RecruitmentDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Recruitment
    serializer_class = RecruitmentSerializer
    roles_required = ['HR', 'ADMIN']

# JobApplication
class JobApplicationListCreateAPIView(BaseListCreateAPIView):
    model = JobApplication
    serializer_class = JobApplicationSerializer
    roles_required = ['HR', 'ADMIN']

class JobApplicationDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = JobApplication
    serializer_class = JobApplicationSerializer
    roles_required = ['HR', 'ADMIN']

# Holiday
class HolidayListCreateAPIView(BaseListCreateAPIView):
    model = Holiday
    serializer_class = HolidaySerializer
    roles_required = ['HR', 'ADMIN']

class HolidayDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Holiday
    serializer_class = HolidaySerializer
    roles_required = ['HR', 'ADMIN']

# WorkSchedule
class WorkScheduleListCreateAPIView(BaseListCreateAPIView):
    model = WorkSchedule
    serializer_class = WorkScheduleSerializer
    roles_required = ['HR', 'ADMIN']

class WorkScheduleDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = WorkSchedule
    serializer_class = WorkScheduleSerializer
    roles_required = ['HR', 'ADMIN']

# TaxConfig
class TaxConfigListCreateAPIView(BaseListCreateAPIView):
    model = TaxConfig
    serializer_class = TaxConfigSerializer
    roles_required = ['HR', 'ADMIN', 'ACCOUNTANT']

class TaxConfigDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = TaxConfig
    serializer_class = TaxConfigSerializer
    roles_required = ['HR', 'ADMIN', 'ACCOUNTANT']

# PFESIConfig
class PFESIConfigListCreateAPIView(BaseListCreateAPIView):
    model = PFESIConfig
    serializer_class = PFESIConfigSerializer
    roles_required = ['HR', 'ADMIN', 'ACCOUNTANT']

class PFESIConfigDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = PFESIConfig
    serializer_class = PFESIConfigSerializer
    roles_required = ['HR', 'ADMIN', 'ACCOUNTANT']

# DisciplinaryAction
class DisciplinaryActionListCreateAPIView(BaseListCreateAPIView):
    model = DisciplinaryAction
    serializer_class = DisciplinaryActionSerializer
    roles_required = ['HR', 'ADMIN']

class DisciplinaryActionDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = DisciplinaryAction
    serializer_class = DisciplinaryActionSerializer
    roles_required = ['HR', 'ADMIN']

# Asset
class AssetListCreateAPIView(BaseListCreateAPIView):
    model = Asset
    serializer_class = AssetSerializer
    roles_required = ['HR', 'ADMIN']

class AssetDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Asset
    serializer_class = AssetSerializer
    roles_required = ['HR', 'ADMIN']

# AssetAssignment
class AssetAssignmentListCreateAPIView(BaseListCreateAPIView):
    model = AssetAssignment
    serializer_class = AssetAssignmentSerializer
    roles_required = ['HR', 'ADMIN']

class AssetAssignmentDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = AssetAssignment
    serializer_class = AssetAssignmentSerializer
    roles_required = ['HR', 'ADMIN']
