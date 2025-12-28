from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from apps.core.api.serializers import TenantAwareSerializer, BaseModelSerializer
from apps.hr.models import (
    Department, Qualification, Designation, Staff, StaffAddress, StaffDocument,
    StaffAttendance, LeaveType, LeaveApplication, LeaveBalance, SalaryStructure,
    Payroll, Promotion, EmploymentHistory, TrainingProgram, TrainingParticipation,
    PerformanceReview, Recruitment, JobApplication, Holiday, WorkSchedule,
    TaxConfig, PFESIConfig, DisciplinaryAction, Asset, AssetAssignment
)

# ============================================================================
# HELPER SERIALIZERS
# ============================================================================

class RelatedFieldAlternative(serializers.PrimaryKeyRelatedField):
    """Serializer field that returns PK by default but full object on request"""
    
    def __init__(self, **kwargs):
        self.serializer = kwargs.pop('serializer', None)
        super().__init__(**kwargs)
    
    def use_pk_only_optimization(self):
        return not self.serializer
    
    def to_representation(self, instance):
        if self.serializer:
            return self.serializer(instance, context=self.context).data
        return super().to_representation(instance)

# ============================================================================
# CORE HR SERIALIZERS
# ============================================================================

class DepartmentSerializer(TenantAwareSerializer):
    staff_count = serializers.IntegerField(read_only=True)
    teacher_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'description', 'head_of_department',
            'email', 'phone', 'location', 
            'staff_count', 'teacher_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'staff_count', 'teacher_count']

class QualificationSerializer(TenantAwareSerializer):
    class Meta:
        model = Qualification
        fields = '__all__'

class DesignationSerializer(TenantAwareSerializer):
    current_holders_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Designation
        fields = [
            'id', 'title', 'code', 'category', 'description',
            'grade', 'min_salary', 'max_salary',
            'qualifications', 'experience_required', 'reports_to',
            'current_holders_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at', 'current_holders_count']

class StaffSerializer(TenantAwareSerializer):
    """
    Serializer for Staff model with detailed representation support
    """
    id = serializers.UUIDField(read_only=True)
    
    # Nested Representations
    department_detail = RelatedFieldAlternative(
        source='department',
        read_only=True,
        serializer=DepartmentSerializer
    )
    designation_detail = RelatedFieldAlternative(
        source='designation',
        read_only=True,
        serializer=DesignationSerializer
    )
    
    # Read-only properties
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    service_years = serializers.IntegerField(read_only=True)
    profile_image = serializers.FileField(read_only=True)
    
    class Meta:
        model = Staff
        fields = [
            'id', 'user', 'employee_id',
            'first_name', 'last_name', 'full_name',
            'date_of_birth', 'age', 'gender', 'blood_group',
            'marital_status', 'nationality',
            'personal_email', 'personal_phone',
            'emergency_contact_name', 'emergency_contact_relation', 'emergency_contact_phone',
            'department', 'department_detail',
            'designation', 'designation_detail',
            'employment_type', 'employment_status',
            'joining_date', 'confirmation_date', 'contract_end_date', 'retirement_date', 'service_years',
            'qualifications', 'specialization', 'teaching_experience', 'total_experience',
            'basic_salary', 'bank_account_number', 'bank_name', 'ifsc_code',
            'pan_number', 'aadhaar_number', 'pf_number', 'esi_number',
            'work_location', 'work_phone', 'work_email',
            'profile_image',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'employee_id', 'full_name', 'age', 'service_years', 'profile_image', 'created_at', 'updated_at']

class StaffAddressSerializer(TenantAwareSerializer):
    staff = serializers.PrimaryKeyRelatedField(queryset=Staff.objects.all())
    
    class Meta:
        model = StaffAddress
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=StaffAddress.objects.all(),
                fields=['staff', 'address_type'],
                message='This type of address already exists for this staff member.'
            )
        ]

class StaffDocumentSerializer(TenantAwareSerializer):
    class Meta:
        model = StaffDocument
        fields = '__all__'

class StaffAttendanceSerializer(TenantAwareSerializer):
    staff_name = serializers.CharField(source='staff.full_name', read_only=True)
    
    class Meta:
        model = StaffAttendance
        fields = '__all__'

# ============================================================================
# LEAVE & PAYROLL SERIALIZERS
# ============================================================================

class LeaveTypeSerializer(TenantAwareSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'

class LeaveApplicationSerializer(TenantAwareSerializer):
    staff_name = serializers.CharField(source='staff.full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)

    class Meta:
        model = LeaveApplication
        fields = '__all__'
        ref_name = "HRLeaveApplication"

class LeaveBalanceSerializer(TenantAwareSerializer):
    class Meta:
        model = LeaveBalance
        fields = '__all__'

class SalaryStructureSerializer(TenantAwareSerializer):
    class Meta:
        model = SalaryStructure
        fields = '__all__'

class PayrollSerializer(TenantAwareSerializer):
    class Meta:
        model = Payroll
        fields = '__all__'

# ============================================================================
# HISTORY & PERFORMANCE SERIALIZERS
# ============================================================================

class PromotionSerializer(TenantAwareSerializer):
    class Meta:
        model = Promotion
        fields = '__all__'

class EmploymentHistorySerializer(TenantAwareSerializer):
    class Meta:
        model = EmploymentHistory
        fields = '__all__'

class TrainingProgramSerializer(TenantAwareSerializer):
    class Meta:
        model = TrainingProgram
        fields = '__all__'

class TrainingParticipationSerializer(TenantAwareSerializer):
    class Meta:
        model = TrainingParticipation
        fields = '__all__'

class PerformanceReviewSerializer(TenantAwareSerializer):
    class Meta:
        model = PerformanceReview
        fields = '__all__'

# ============================================================================
# RECRUITMENT SERIALIZERS
# ============================================================================

class RecruitmentSerializer(TenantAwareSerializer):
    class Meta:
        model = Recruitment
        fields = '__all__'

class JobApplicationSerializer(TenantAwareSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'

# ============================================================================
# CONFIG SERIALIZERS
# ============================================================================

class HolidaySerializer(TenantAwareSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'
        ref_name = "HRHoliday"

class WorkScheduleSerializer(TenantAwareSerializer):
    class Meta:
        model = WorkSchedule
        fields = '__all__'

class TaxConfigSerializer(TenantAwareSerializer):
    class Meta:
        model = TaxConfig
        fields = '__all__'

class PFESIConfigSerializer(TenantAwareSerializer):
    class Meta:
        model = PFESIConfig
        fields = '__all__'

class DisciplinaryActionSerializer(TenantAwareSerializer):
    class Meta:
        model = DisciplinaryAction
        fields = '__all__'

class AssetSerializer(TenantAwareSerializer):
    class Meta:
        model = Asset
        fields = '__all__'
        ref_name = "HRAsset"

class AssetAssignmentSerializer(TenantAwareSerializer):
    class Meta:
        model = AssetAssignment
        fields = '__all__'
