from django.urls import path
from .views import (
    DepartmentListCreateAPIView, DepartmentDetailAPIView,
    QualificationListCreateAPIView, QualificationDetailAPIView,
    DesignationListCreateAPIView, DesignationDetailAPIView,
    StaffListCreateAPIView, StaffDetailAPIView,
    StaffAddressListCreateAPIView, StaffAddressDetailAPIView,
    StaffDocumentListCreateAPIView, StaffDocumentDetailAPIView,
    StaffAttendanceListCreateAPIView, StaffAttendanceDetailAPIView,
    LeaveTypeListCreateAPIView, LeaveTypeDetailAPIView,
    LeaveApplicationListCreateAPIView, LeaveApplicationDetailAPIView,
    LeaveBalanceListCreateAPIView, LeaveBalanceDetailAPIView,
    SalaryStructureListCreateAPIView, SalaryStructureDetailAPIView,
    PayrollListCreateAPIView, PayrollDetailAPIView,
    PromotionListCreateAPIView, PromotionDetailAPIView,
    EmploymentHistoryListCreateAPIView, EmploymentHistoryDetailAPIView,
    TrainingProgramListCreateAPIView, TrainingProgramDetailAPIView,
    TrainingParticipationListCreateAPIView, TrainingParticipationDetailAPIView,
    PerformanceReviewListCreateAPIView, PerformanceReviewDetailAPIView,
    RecruitmentListCreateAPIView, RecruitmentDetailAPIView,
    JobApplicationListCreateAPIView, JobApplicationDetailAPIView,
    HolidayListCreateAPIView, HolidayDetailAPIView,
    WorkScheduleListCreateAPIView, WorkScheduleDetailAPIView,
    TaxConfigListCreateAPIView, TaxConfigDetailAPIView,
    PFESIConfigListCreateAPIView, PFESIConfigDetailAPIView,
    DisciplinaryActionListCreateAPIView, DisciplinaryActionDetailAPIView,
    AssetListCreateAPIView, AssetDetailAPIView,
    AssetAssignmentListCreateAPIView, AssetAssignmentDetailAPIView
)

from .dashboard_view import StaffDashboardAPIView

urlpatterns = [
    # Dashboard
    path('dashboard/', StaffDashboardAPIView.as_view(), name='dashboard'),

    # Department
    path('departments/', DepartmentListCreateAPIView.as_view(), name='department-list'),
    path('departments/<uuid:pk>/', DepartmentDetailAPIView.as_view(), name='department-detail'),

    # Qualification
    path('qualifications/', QualificationListCreateAPIView.as_view(), name='qualification-list'),
    path('qualifications/<uuid:pk>/', QualificationDetailAPIView.as_view(), name='qualification-detail'),

    # Designation
    path('designations/', DesignationListCreateAPIView.as_view(), name='designation-list'),
    path('designations/<uuid:pk>/', DesignationDetailAPIView.as_view(), name='designation-detail'),

    # Staff
    path('staff/', StaffListCreateAPIView.as_view(), name='staff-list'),
    path('staff/<uuid:pk>/', StaffDetailAPIView.as_view(), name='staff-detail'),

    # Staff Address
    path('staff-addresses/', StaffAddressListCreateAPIView.as_view(), name='staff-address-list'),
    path('staff-addresses/<uuid:pk>/', StaffAddressDetailAPIView.as_view(), name='staff-address-detail'),

    # Staff Document
    path('staff-documents/', StaffDocumentListCreateAPIView.as_view(), name='staff-document-list'),
    path('staff-documents/<uuid:pk>/', StaffDocumentDetailAPIView.as_view(), name='staff-document-detail'),

    # Staff Attendance
    path('attendance/', StaffAttendanceListCreateAPIView.as_view(), name='staff-attendance-list'),
    path('attendance/<uuid:pk>/', StaffAttendanceDetailAPIView.as_view(), name='staff-attendance-detail'),

    # Leave Type
    path('leave-types/', LeaveTypeListCreateAPIView.as_view(), name='leave-type-list'),
    path('leave-types/<uuid:pk>/', LeaveTypeDetailAPIView.as_view(), name='leave-type-detail'),

    # Leave Application
    path('leave-applications/', LeaveApplicationListCreateAPIView.as_view(), name='leave-application-list'),
    path('leave-applications/<uuid:pk>/', LeaveApplicationDetailAPIView.as_view(), name='leave-application-detail'),

    # Leave Balance
    path('leave-balances/', LeaveBalanceListCreateAPIView.as_view(), name='leave-balance-list'),
    path('leave-balances/<uuid:pk>/', LeaveBalanceDetailAPIView.as_view(), name='leave-balance-detail'),

    # Salary Structure
    path('salary-structures/', SalaryStructureListCreateAPIView.as_view(), name='salary-structure-list'),
    path('salary-structures/<uuid:pk>/', SalaryStructureDetailAPIView.as_view(), name='salary-structure-detail'),

    # Payroll
    path('payrolls/', PayrollListCreateAPIView.as_view(), name='payroll-list'),
    path('payrolls/<uuid:pk>/', PayrollDetailAPIView.as_view(), name='payroll-detail'),

    # Promotion
    path('promotions/', PromotionListCreateAPIView.as_view(), name='promotion-list'),
    path('promotions/<uuid:pk>/', PromotionDetailAPIView.as_view(), name='promotion-detail'),

    # Employment History
    path('employment-history/', EmploymentHistoryListCreateAPIView.as_view(), name='employment-history-list'),
    path('employment-history/<uuid:pk>/', EmploymentHistoryDetailAPIView.as_view(), name='employment-history-detail'),

    # Training Program
    path('training-programs/', TrainingProgramListCreateAPIView.as_view(), name='training-program-list'),
    path('training-programs/<uuid:pk>/', TrainingProgramDetailAPIView.as_view(), name='training-program-detail'),

    # Training Participation
    path('training-participations/', TrainingParticipationListCreateAPIView.as_view(), name='training-participation-list'),
    path('training-participations/<uuid:pk>/', TrainingParticipationDetailAPIView.as_view(), name='training-participation-detail'),

    # Performance Review
    path('performance-reviews/', PerformanceReviewListCreateAPIView.as_view(), name='performance-review-list'),
    path('performance-reviews/<uuid:pk>/', PerformanceReviewDetailAPIView.as_view(), name='performance-review-detail'),

    # Recruitment
    path('recruitments/', RecruitmentListCreateAPIView.as_view(), name='recruitment-list'),
    path('recruitments/<uuid:pk>/', RecruitmentDetailAPIView.as_view(), name='recruitment-detail'),

    # Job Application
    path('job-applications/', JobApplicationListCreateAPIView.as_view(), name='job-application-list'),
    path('job-applications/<uuid:pk>/', JobApplicationDetailAPIView.as_view(), name='job-application-detail'),

    # Holiday
    path('holidays/', HolidayListCreateAPIView.as_view(), name='holiday-list'),
    path('holidays/<uuid:pk>/', HolidayDetailAPIView.as_view(), name='holiday-detail'),

    # Work Schedule
    path('work-schedules/', WorkScheduleListCreateAPIView.as_view(), name='work-schedule-list'),
    path('work-schedules/<uuid:pk>/', WorkScheduleDetailAPIView.as_view(), name='work-schedule-detail'),

    # Tax Config
    path('tax-configs/', TaxConfigListCreateAPIView.as_view(), name='tax-config-list'),
    path('tax-configs/<uuid:pk>/', TaxConfigDetailAPIView.as_view(), name='tax-config-detail'),

    # PFESI Config
    path('pfesi-configs/', PFESIConfigListCreateAPIView.as_view(), name='pfesi-config-list'),
    path('pfesi-configs/<uuid:pk>/', PFESIConfigDetailAPIView.as_view(), name='pfesi-config-detail'),

    # Disciplinary Action
    path('disciplinary-actions/', DisciplinaryActionListCreateAPIView.as_view(), name='disciplinary-action-list'),
    path('disciplinary-actions/<uuid:pk>/', DisciplinaryActionDetailAPIView.as_view(), name='disciplinary-action-detail'),

    # Asset
    path('assets/', AssetListCreateAPIView.as_view(), name='asset-list'),
    path('assets/<uuid:pk>/', AssetDetailAPIView.as_view(), name='asset-detail'),

    # Asset Assignment
    path('asset-assignments/', AssetAssignmentListCreateAPIView.as_view(), name='asset-assignment-list'),
    path('asset-assignments/<uuid:pk>/', AssetAssignmentDetailAPIView.as_view(), name='asset-assignment-detail'),
]
