# In apps/students/api/serializers.py
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from django.conf import settings

# Models
from apps.students.models import (
    Student, Guardian, StudentAddress, StudentDocument,
    StudentMedicalInfo, StudentAcademicHistory, StudentIdentification
)
from apps.academics.models import SchoolClass, Section, AcademicYear
from apps.users.models import User

# Core serializers
from apps.core.api.serializers import BaseModelSerializer, TenantAwareSerializer
from apps.core.utils.validators import (
    validate_phone_number, validate_aadhaar_number, validate_pan_number,
    validate_ifsc_code, validate_date_not_future
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
# RELATED MODEL SERIALIZERS
# ============================================================================

class GuardianSerializer(TenantAwareSerializer):
    """Serializer for Guardian model"""
    
    id = serializers.UUIDField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        required=True,
        write_only=True
    )
    student_detail = RelatedFieldAlternative(
        source='student',
        read_only=True,
        serializer='StudentListSerializer'
    )
    
    # Phone validation
    phone_primary = serializers.CharField(
        validators=[validate_phone_number],
        max_length=17
    )
    phone_secondary = serializers.CharField(
        validators=[validate_phone_number],
        max_length=17,
        required=False,
        allow_blank=True
    )
    
    # Encrypted fields
    aadhaar_number = serializers.CharField(
        max_length=12,
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[validate_aadhaar_number]
    )
    pan_number = serializers.CharField(
        max_length=10,
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[validate_pan_number]
    )
    
    # Age property
    age = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Guardian
        fields = [
            'id', 'student', 'student_detail',
            'relation', 'full_name', 'date_of_birth', 'age',
            'email', 'phone_primary', 'phone_secondary',
            'occupation', 'qualification', 'company_name', 'designation',
            'annual_income', 'is_primary', 'is_emergency_contact',
            'can_pickup', 'aadhaar_number', 'pan_number',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'age', 'created_at', 'updated_at']
        validators = [
            UniqueTogetherValidator(
                queryset=Guardian.objects.all(),
                fields=['student', 'relation'],
                message=_('A guardian with this relation already exists for this student.')
            )
        ]
    
    def validate(self, data):
        """Additional validation for guardian data"""
        # Check if primary guardian already exists
        if data.get('is_primary', False):
            existing_primary = Guardian.objects.filter(
                student=data.get('student'),
                is_primary=True
            ).exclude(id=self.instance.id if self.instance else None)
            
            if existing_primary.exists():
                raise serializers.ValidationError({
                    'is_primary': _('This student already has a primary guardian.')
                })
        
        # Check if emergency contact already exists
        if data.get('is_emergency_contact', False):
            existing_emergency = Guardian.objects.filter(
                student=data.get('student'),
                is_emergency_contact=True
            ).exclude(id=self.instance.id if self.instance else None)
            
            if existing_emergency.exists():
                raise serializers.ValidationError({
                    'is_emergency_contact': _('This student already has an emergency contact.')
                })
        
        return data


class StudentAddressSerializer(TenantAwareSerializer):
    """Serializer for StudentAddress model"""
    
    id = serializers.UUIDField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        required=True,
        write_only=True
    )
    student_detail = RelatedFieldAlternative(
        source='student',
        read_only=True,
        serializer='StudentListSerializer'
    )
    
    # Formatted address
    formatted_address = serializers.CharField(read_only=True)
    google_maps_url = serializers.CharField(read_only=True)
    
    # Pincode validation
    pincode = serializers.CharField(
        max_length=10,
        validators=[RegexValidator(
            regex=r'^\d{6}$',
            message=_('Enter a valid 6-digit pincode')
        )]
    )
    
    class Meta:
        model = StudentAddress
        fields = [
            'id', 'student', 'student_detail',
            'address_type', 'address_line1', 'address_line2',
            'landmark', 'city', 'state', 'pincode', 'country',
            'latitude', 'longitude', 'is_current', 'is_verified',
            'formatted_address', 'google_maps_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'formatted_address', 'google_maps_url', 'created_at', 'updated_at']
        validators = [
            UniqueTogetherValidator(
                queryset=StudentAddress.objects.all(),
                fields=['student', 'address_type'],
                message=_('This type of address already exists for this student.')
            )
        ]
    
    def validate(self, data):
        """Address validation"""
        # If making address current, update other addresses
        if data.get('is_current', False):
            StudentAddress.objects.filter(
                student=data.get('student'),
                is_current=True
            ).exclude(id=self.instance.id if self.instance else None).update(is_current=False)
        
        # Permanent addresses should be verified
        if data.get('address_type') == 'PERMANENT':
            data['is_verified'] = True
        
        return data


class StudentDocumentSerializer(TenantAwareSerializer):
    """Serializer for StudentDocument model"""
    
    id = serializers.UUIDField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        required=True,
        write_only=True
    )
    student_detail = RelatedFieldAlternative(
        source='student',
        read_only=True,
        serializer='StudentListSerializer'
    )
    
    # File handling
    file = serializers.FileField(
        max_length=255,
        required=False  # Not required for updates
    )
    file_url = serializers.SerializerMethodField()
    file_name = serializers.CharField(read_only=True)
    file_size = serializers.IntegerField(read_only=True)
    
    # Document verification
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)
    download_url = serializers.CharField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = StudentDocument
        fields = [
            'id', 'student', 'student_detail',
            'doc_type', 'file', 'file_url', 'file_name', 'file_size', 'file_hash',
            'description', 'issue_date', 'expiry_date', 'issuing_authority',
            'status', 'is_verified', 'verified_by', 'verified_by_name',
            'verified_at', 'rejection_reason', 'version', 'is_current',
            'previous_version', 'download_url', 'is_expired',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_name', 'file_size', 'file_hash', 'status',
            'is_verified', 'verified_by', 'verified_at', 'rejection_reason',
            'version', 'is_current', 'previous_version', 'download_url',
            'is_expired', 'created_at', 'updated_at'
        ]
    
    def get_file_url(self, obj):
        """Get file URL if file exists"""
        if obj.file:
            return obj.file.url
        return None
    
    def validate_file(self, value):
        """Validate uploaded file"""
        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                _('File size must be less than 10MB')
            )
        
        # Check file extension
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
        ext = value.name.split('.')[-1].lower()
        if f'.{ext}' not in allowed_extensions:
            raise serializers.ValidationError(
                _('File type not allowed. Allowed types: PDF, JPG, PNG, DOC, DOCX')
            )
        
        return value
    
    def create(self, validated_data):
        """Create document with versioning"""
        # Check if document type already exists
        student = validated_data['student']
        doc_type = validated_data['doc_type']
        
        existing_doc = StudentDocument.objects.filter(
            student=student,
            doc_type=doc_type,
            is_current=True
        ).first()
        
        if existing_doc:
            # Increment version
            validated_data['version'] = existing_doc.version + 1
            validated_data['previous_version'] = existing_doc
            
            # Mark previous version as not current
            existing_doc.is_current = False
            existing_doc.save()
        
        return super().create(validated_data)


class StudentMedicalInfoSerializer(TenantAwareSerializer):
    """Serializer for StudentMedicalInfo model"""
    
    id = serializers.UUIDField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        required=True,
        write_only=True
    )
    student_detail = RelatedFieldAlternative(
        source='student',
        read_only=True,
        serializer='StudentListSerializer'
    )
    
    # Calculated fields
    bmi_category = serializers.CharField(read_only=True)
    
    # Phone validation
    emergency_contact_phone = serializers.CharField(
        validators=[validate_phone_number],
        max_length=17,
        required=False,
        allow_blank=True
    )
    emergency_contact_alt_phone = serializers.CharField(
        validators=[validate_phone_number],
        max_length=17,
        required=False,
        allow_blank=True
    )
    
    # JSON field
    vaccination_records = serializers.JSONField(
        required=False,
        default=dict
    )
    
    class Meta:
        model = StudentMedicalInfo
        fields = [
            'id', 'student', 'student_detail',
            'blood_group', 'height_cm', 'weight_kg', 'bmi', 'bmi_category',
            'known_allergies', 'chronic_conditions', 'current_medications',
            'dietary_restrictions', 'has_disability', 'disability_type',
            'disability_percentage', 'disability_certificate_number',
            'vaccination_records', 'emergency_contact_name',
            'emergency_contact_relation', 'emergency_contact_phone',
            'emergency_contact_alt_phone', 'has_medical_insurance',
            'insurance_provider', 'insurance_policy_number',
            'insurance_valid_until', 'special_instructions',
            'last_medical_checkup', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'bmi', 'bmi_category', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Medical info validation"""
        # Disability validation
        if data.get('has_disability', False) and not data.get('disability_type'):
            raise serializers.ValidationError({
                'disability_type': _('Disability type is required when disability is marked.')
            })
        
        # Insurance validation
        if data.get('has_medical_insurance', False) and not data.get('insurance_provider'):
            raise serializers.ValidationError({
                'insurance_provider': _('Insurance provider is required when insurance is marked.')
            })
        
        return data
    
    def to_representation(self, instance):
        """Custom representation for medical info"""
        data = super().to_representation(instance)
        
        # Add emergency info summary
        data['emergency_info'] = instance.get_emergency_info()
        
        return data


class StudentAcademicHistorySerializer(TenantAwareSerializer):
    """Serializer for StudentAcademicHistory model"""
    
    id = serializers.UUIDField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        required=True,
        write_only=True
    )
    student_detail = RelatedFieldAlternative(
        source='student',
        read_only=True,
        serializer='StudentListSerializer'
    )
    
    # Related fields
    academic_year_name = serializers.CharField(
        source='academic_year.name',
        read_only=True
    )
    class_name_display = serializers.CharField(
        source='class_name.name',
        read_only=True
    )
    section_name = serializers.CharField(
        source='section.name',
        read_only=True
    )
    
    class Meta:
        model = StudentAcademicHistory
        fields = [
            'id', 'student', 'student_detail',
            'academic_year', 'academic_year_name',
            'class_name', 'class_name_display',
            'section', 'section_name',
            'roll_number', 'overall_grade', 'percentage',
            'result', 'remarks', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'academic_year_name', 'class_name_display',
            'section_name', 'created_at', 'updated_at'
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=StudentAcademicHistory.objects.all(),
                fields=['student', 'academic_year'],
                message=_('Academic history for this year already exists.')
            )
        ]
    
    def validate_percentage(self, value):
        """Validate percentage"""
        if value is not None:
            if value < 0 or value > 100:
                raise serializers.ValidationError(
                    _('Percentage must be between 0 and 100.')
                )
        return value


class StudentIdentificationSerializer(TenantAwareSerializer):
    """Serializer for StudentIdentification model"""
    
    id = serializers.UUIDField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        required=True,
        write_only=True
    )
    student_detail = RelatedFieldAlternative(
        source='student',
        read_only=True,
        serializer='StudentListSerializer'
    )
    
    # Encrypted fields
    aadhaar_number = serializers.CharField(
        max_length=12,
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[validate_aadhaar_number]
    )
    pan_number = serializers.CharField(
        max_length=10,
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[validate_pan_number]
    )
    bank_account_number = serializers.CharField(
        max_length=20,
        required=False,
        allow_null=True,
        allow_blank=True
    )
    
    # Bank validation
    ifsc_code = serializers.CharField(
        max_length=11,
        required=False,
        allow_blank=True,
        validators=[validate_ifsc_code]
    )
    
    # Read-only computed field
    has_complete_identification = serializers.BooleanField(read_only=True)
    identification_summary = serializers.JSONField(read_only=True)
    
    class Meta:
        model = StudentIdentification
        fields = [
            'id', 'student', 'student_detail',
            'aadhaar_number', 'aadhaar_verified',
            'pan_number', 'pan_verified',
            'passport_number', 'passport_verified',
            'driving_license', 'voter_id',
            'abc_id', 'shiksha_id', 'udise_id',
            'bank_account_number', 'bank_name', 'bank_branch', 'ifsc_code',
            'social_security_number', 'national_insurance_number',
            'has_complete_identification', 'identification_summary',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'aadhaar_verified', 'pan_verified', 'passport_verified',
            'has_complete_identification', 'identification_summary',
            'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        """Validate identification data"""
        # If Aadhaar is provided, mark it as verified if not already
        if 'aadhaar_number' in data and data['aadhaar_number']:
            if self.instance and not self.instance.aadhaar_verified:
                data['aadhaar_verified'] = True
            elif not self.instance:
                data['aadhaar_verified'] = True
        
        # If PAN is provided, mark it as verified if not already
        if 'pan_number' in data and data['pan_number']:
            if self.instance and not self.instance.pan_verified:
                data['pan_verified'] = True
            elif not self.instance:
                data['pan_verified'] = True
        
        return data


# ============================================================================
# MAIN STUDENT SERIALIZERS
# ============================================================================

class StudentListSerializer(TenantAwareSerializer):
    """Lightweight serializer for listing students"""
    
    id = serializers.UUIDField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    
    # Related field information
    current_class_name = serializers.CharField(
        source='current_class.name',
        read_only=True,
        default=''
    )
    section_name = serializers.CharField(
        source='section.name',
        read_only=True,
        default=''
    )
    
    # Contact information
    email = serializers.EmailField(source='personal_email')
    phone = serializers.CharField(source='mobile_primary')
    
    # Status
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    # Quick actions
    has_required_documents = serializers.BooleanField(read_only=True)
    is_eligible_for_exams = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'admission_number', 'roll_number', 'reg_no',
            'full_name', 'first_name', 'last_name', 'age',
            'date_of_birth', 'gender', 'blood_group',
            'current_class', 'current_class_name',
            'section', 'section_name',
            'email', 'phone',
            'status', 'status_display',
            'enrollment_date', 'academic_year',
            'has_required_documents', 'is_eligible_for_exams',
            'created_at'
        ]
        read_only_fields = [
            'id', 'full_name', 'age', 'current_class_name',
            'section_name', 'status_display', 'has_required_documents',
            'is_eligible_for_exams', 'created_at'
        ]


class StudentDetailSerializer(TenantAwareSerializer):
    """Detailed serializer for student with nested relations"""
    
    id = serializers.UUIDField(read_only=True)
    
    # Core fields
    admission_number = serializers.CharField(read_only=True)
    roll_number = serializers.CharField(read_only=True)
    reg_no = serializers.CharField(read_only=True)
    
    # Personal information
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    academic_age = serializers.IntegerField(read_only=True)
    
    # Phone validation
    mobile_primary = serializers.CharField(
        validators=[validate_phone_number],
        max_length=17
    )
    mobile_secondary = serializers.CharField(
        validators=[validate_phone_number],
        max_length=17,
        required=False,
        allow_blank=True
    )
    
    # Email uniqueness validation
    personal_email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=Student.objects.all(),
                message=_('A student with this email already exists.')
            )
        ]
    )
    
    # Related field information
    current_class_name = serializers.CharField(
        source='current_class.name',
        read_only=True,
        default=''
    )
    section_name = serializers.CharField(
        source='section.name',
        read_only=True,
        default=''
    )
    
    # Address information
    current_address = serializers.CharField(read_only=True)
    permanent_address = serializers.CharField(read_only=True)
    
    # Nested serializers
    guardians = GuardianSerializer(
        many=True,
        read_only=True,
        source='guardians.all'
    )
    addresses = StudentAddressSerializer(
        many=True,
        read_only=True,
        source='addresses.all'
    )
    documents = StudentDocumentSerializer(
        many=True,
        read_only=True,
        source='documents.filter(is_current=True)'
    )
    medical_info = StudentMedicalInfoSerializer(
        read_only=True,
        source='medical_info'
    )
    academic_history = StudentAcademicHistorySerializer(
        many=True,
        read_only=True,
        source='academic_history.all'
    )
    identification = StudentIdentificationSerializer(
        read_only=True,
        source='identification'
    )
    
    # Academic performance
    attendance_percentage = serializers.SerializerMethodField()
    academic_performance = serializers.SerializerMethodField()
    
    # System fields
    user_account = serializers.SerializerMethodField()
    onboarding_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            # Core Identification
            'id', 'user', 'admission_number', 'roll_number', 'reg_no',
            
            # Personal Information
            'first_name', 'middle_name', 'last_name', 'full_name',
            'date_of_birth', 'place_of_birth', 'age', 'gender',
            'blood_group', 'nationality', 'marital_status',
            
            # Contact Information
            'personal_email', 'institutional_email',
            'mobile_primary', 'mobile_secondary',
            
            # Academic Information
            'admission_type', 'enrollment_date', 'academic_age',
            'academic_year', 'current_class', 'current_class_name',
            'stream', 'section', 'section_name',
            'current_semester', 'total_credits_earned', 'cumulative_grade_point',
            
            # Socio-economic Information
            'category', 'religion', 'is_minority', 'is_physically_challenged',
            'annual_family_income',
            
            # Status & Tracking
            'status', 'status_changed_date', 'passing_year', 'tc_issue_date',
            'status_display',
            
            # Fee & Financial
            'fee_category', 'scholarship_type',
            
            # Address Information
            'current_address', 'permanent_address',
            
            # Nested Relations
            'guardians', 'addresses', 'documents', 'medical_info',
            'academic_history', 'identification',
            
            # Academic Performance
            'attendance_percentage', 'academic_performance',
            
            # System Information
            'user_account', 'created_at', 'updated_at',
            'user_account', 'created_at', 'updated_at',
            'created_by', 'updated_by',
             # Onboarding
            'onboarding_summary'
        ]
        read_only_fields = [
            'id', 'admission_number', 'roll_number', 'reg_no',
            'full_name', 'age', 'academic_age', 'current_class_name',
            'section_name', 'institutional_email', 'status_display',
            'current_address', 'permanent_address',
            'guardians', 'addresses', 'documents', 'medical_info',
            'academic_history', 'identification',
            'attendance_percentage', 'academic_performance',
            'user_account', 'created_at', 'updated_at',
            'created_by', 'updated_by', 'onboarding_summary'
        ]
    
    def get_onboarding_summary(self, obj):
        """Calculate onboarding progress status matching Django view logic"""
        steps = [
            {
                'id': 'basic',
                'title': _('Basic Information'),
                'is_completed': True, 
            },
            {
                'id': 'guardian',
                'title': _('Guardian Details'),
                'is_completed': obj.guardians.exists(),
            },
            {
                'id': 'address',
                'title': _('Address Details'),
                'is_completed': obj.addresses.exists(),
            },
            {
                'id': 'medical',
                'title': _('Medical Information'),
                'is_completed': hasattr(obj, 'medical_info'),
            },
            {
                'id': 'documents',
                'title': _('Documents'),
                'is_completed': obj.documents.exists(),
            },
            {
                'id': 'identification',
                'title': _('Identification'),
                'is_completed': hasattr(obj, 'identification') and obj.identification.has_complete_identification,
            },
            {
                'id': 'transport',
                'title': _('Transport'),
                'is_completed': hasattr(obj, 'transport_allocation') and obj.transport_allocation.is_active,
                'optional': True
            },
            {
                'id': 'hostel',
                'title': _('Hostel'),
                'is_completed': hasattr(obj, 'hostel_allocation') and obj.hostel_allocation.is_active,
                'optional': True
            },
             {
                'id': 'history',
                'title': _('Academic History'),
                'is_completed': obj.academic_history.exists(),
                'optional': True
            },
            {
                'id': 'account',
                'title': _('Account Info'),
                'is_completed': obj.user is not None,
            }
        ]
        
        required_steps = [s for s in steps if not s.get('optional')]
        completed_required = len([s for s in required_steps if s['is_completed']])
        progress = (completed_required / len(required_steps) * 100) if required_steps else 0
        
        return {
            'progress': progress,
            'is_complete': progress == 100,
            'steps': steps
        }
    
    def get_attendance_percentage(self, obj):
        """Get current academic year attendance percentage"""
        request = self.context.get('request')
        if request and 'start_date' in request.query_params:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            return obj.get_attendance_percentage(start_date, end_date)
        return obj.get_attendance_percentage()
    
    def get_academic_performance(self, obj):
        """Get academic performance summary"""
        return obj.get_academic_performance()
    
    def get_user_account(self, obj):
        """Get user account information"""
        if obj.user:
            return {
                'id': obj.user.id,
                'email': obj.user.email,
                'username': obj.user.username,
                'is_active': obj.user.is_active,
                'last_login': obj.user.last_login
            }
        return None
    
    def validate(self, data):
        """Custom validation for student data"""
        errors = {}
        
        # Date validations
        today = timezone.now().date()
        
        if 'date_of_birth' in data:
            if data['date_of_birth'] >= today:
                errors['date_of_birth'] = _('Date of birth must be in the past.')
            
            # Calculate age
            age = today.year - data['date_of_birth'].year - (
                (today.month, today.day) < (data['date_of_birth'].month, data['date_of_birth'].day)
            )
            if age < 3:
                errors['date_of_birth'] = _('Student must be at least 3 years old.')
        
        if 'enrollment_date' in data:
            if data['enrollment_date'] > today:
                errors['enrollment_date'] = _('Enrollment date cannot be in the future.')
        
        # Email domain validation (optional)
        if 'personal_email' in data:
            # Check if email is from valid domains
            invalid_domains = ['tempmail.com', 'yopmail.com']
            domain = data['personal_email'].split('@')[-1]
            if domain in invalid_domains:
                errors['personal_email'] = _('Temporary email addresses are not allowed.')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class StudentCreateSerializer(StudentDetailSerializer):
    """Serializer for creating students with related data"""
    
    # For creation, we need writeable nested serializers
    guardians = GuardianSerializer(
        many=True,
        required=False
    )
    addresses = StudentAddressSerializer(
        many=True,
        required=False
    )
    medical_info = StudentMedicalInfoSerializer(
        required=False
    )
    identification = StudentIdentificationSerializer(
        required=False
    )
    
    # For creating user account
    create_user_account = serializers.BooleanField(
        default=True,
        write_only=True,
        help_text=_('Create a user account for the student')
    )
    send_welcome_email = serializers.BooleanField(
        default=True,
        write_only=True,
        help_text=_('Send welcome email with credentials')
    )
    
    class Meta:
        model = Student
        fields = StudentDetailSerializer.Meta.fields + [
            'guardians', 'addresses', 'medical_info', 'identification',
            'create_user_account', 'send_welcome_email'
        ]
    
    def validate(self, data):
        """Validation for student creation"""
        data = super().validate(data)
        
        # Ensure at least one guardian is marked as primary
        guardians = data.get('guardians', [])
        if guardians:
            primary_guardians = [g for g in guardians if g.get('is_primary', False)]
            if not primary_guardians:
                raise serializers.ValidationError({
                    'guardians': _('At least one guardian must be marked as primary.')
                })
        
        # Ensure at least one address is marked as current
        addresses = data.get('addresses', [])
        if addresses:
            current_addresses = [a for a in addresses if a.get('is_current', False)]
            if not current_addresses:
                raise serializers.ValidationError({
                    'addresses': _('At least one address must be marked as current.')
                })
        
        # Ensure permanent address exists
        permanent_addresses = [a for a in addresses if a.get('address_type') == 'PERMANENT']
        if not permanent_addresses:
            raise serializers.ValidationError({
                'addresses': _('A permanent address is required.')
            })
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        """Create student with all related data"""
        # Extract nested data
        guardians_data = validated_data.pop('guardians', [])
        addresses_data = validated_data.pop('addresses', [])
        medical_info_data = validated_data.pop('medical_info', None)
        identification_data = validated_data.pop('identification', None)
        
        create_user_account = validated_data.pop('create_user_account', True)
        send_welcome_email = validated_data.pop('send_welcome_email', True)
        
        # Create student
        student = Student.objects.create(**validated_data)
        
        # Create guardians
        for guardian_data in guardians_data:
            Guardian.objects.create(student=student, **guardian_data)
        
        # Create addresses
        for address_data in addresses_data:
            StudentAddress.objects.create(student=student, **address_data)
        
        # Create medical info
        if medical_info_data:
            StudentMedicalInfo.objects.create(student=student, **medical_info_data)
        
        # Create identification
        if identification_data:
            StudentIdentification.objects.create(student=student, **identification_data)
        
        # Create user account if requested
        if create_user_account:
            try:
                student.create_user_account()
                if send_welcome_email and student.personal_email:
                    # Email sending would happen in create_user_account method
                    pass
            except Exception as e:
                # Log error but don't fail student creation
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to create user account for student {student.id}: {e}")
        
        return student


class StudentUpdateSerializer(StudentDetailSerializer):
    """Serializer for updating students"""
    
    class Meta:
        model = Student
        fields = StudentDetailSerializer.Meta.fields
        read_only_fields = StudentDetailSerializer.Meta.read_only_fields + [
            'admission_number', 'roll_number', 'reg_no', 'personal_email'
        ]
    
    def update(self, instance, validated_data):
        """Update student instance"""
        # Handle status change
        if 'status' in validated_data and instance.status != validated_data['status']:
            validated_data['status_changed_date'] = timezone.now()
        
        return super().update(instance, validated_data)


# ============================================================================
# SPECIALIZED SERIALIZERS
# ============================================================================

class StudentBulkCreateSerializer(TenantAwareSerializer):
    """Serializer for bulk student creation via CSV/Excel"""
    
    students = StudentCreateSerializer(many=True)
    
    class Meta:
        fields = ['students']
    
    def create(self, validated_data):
        """Create multiple students"""
        students_data = validated_data['students']
        created_students = []
        
        with transaction.atomic():
            for student_data in students_data:
                serializer = StudentCreateSerializer(
                    data=student_data,
                    context=self.context
                )
                serializer.is_valid(raise_exception=True)
                student = serializer.save()
                created_students.append(student)
        
        return {'created': len(created_students), 'students': created_students}


class StudentImportSerializer(serializers.Serializer):
    """Serializer for importing students from CSV/Excel"""
    
    file = serializers.FileField()
    create_user_accounts = serializers.BooleanField(default=False)
    send_welcome_emails = serializers.BooleanField(default=False)
    
    def validate_file(self, value):
        """Validate uploaded file"""
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        ext = value.name.split('.')[-1].lower()
        if f'.{ext}' not in allowed_extensions:
            raise serializers.ValidationError(
                _('File type not allowed. Allowed types: CSV, XLSX, XLS')
            )
        
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                _('File size must be less than 10MB')
            )
        
        return value


class StudentExportSerializer(serializers.ModelSerializer):
    """Serializer for student data export"""
    
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    current_class_name = serializers.CharField(source='current_class.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    guardian_name = serializers.SerializerMethodField()
    guardian_phone = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'admission_number', 'roll_number', 'full_name',
            'first_name', 'middle_name', 'last_name',
            'date_of_birth', 'age', 'gender', 'blood_group',
            'personal_email', 'institutional_email',
            'mobile_primary', 'mobile_secondary',
            'current_class_name', 'section_name',
            'admission_type', 'enrollment_date',
            'category', 'religion', 'is_minority', 'is_physically_challenged',
            'status', 'status_display',
            'guardian_name', 'guardian_phone', 'address',
            'created_at'
        ]
    
    def get_guardian_name(self, obj):
        """Get primary guardian name"""
        primary_guardian = obj.guardians.filter(is_primary=True).first()
        return primary_guardian.full_name if primary_guardian else ''
    
    def get_guardian_phone(self, obj):
        """Get primary guardian phone"""
        primary_guardian = obj.guardians.filter(is_primary=True).first()
        return primary_guardian.phone_primary if primary_guardian else ''
    
    def get_address(self, obj):
        """Get current address"""
        current_address = obj.addresses.filter(is_current=True).first()
        return current_address.formatted_address if current_address else ''


class StudentStatisticsSerializer(serializers.Serializer):
    """Serializer for student statistics"""
    
    total_students = serializers.IntegerField()
    active_students = serializers.IntegerField()
    inactive_students = serializers.IntegerField()
    alumni_students = serializers.IntegerField()
    suspended_students = serializers.IntegerField()
    
    # Gender distribution
    male_students = serializers.IntegerField()
    female_students = serializers.IntegerField()
    other_gender_students = serializers.IntegerField()
    
    # Class distribution
    class_distribution = serializers.DictField(
        child=serializers.IntegerField()
    )
    
    # Category distribution
    category_distribution = serializers.DictField(
        child=serializers.IntegerField()
    )
    
    # Monthly enrollment trend
    monthly_enrollment = serializers.DictField(
        child=serializers.IntegerField()
    )
    
    # Average age
    average_age = serializers.FloatField()
    
    # Document compliance
    with_required_documents = serializers.IntegerField()
    without_required_documents = serializers.IntegerField()
    
    def to_representation(self, instance):
        """Convert statistics to representation"""
        return instance


class StudentPromotionSerializer(serializers.Serializer):
    """Serializer for student promotion"""
    
    student_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    target_class = serializers.PrimaryKeyRelatedField(
        queryset=SchoolClass.objects.all()
    )
    target_section = serializers.PrimaryKeyRelatedField(
        queryset=Section.objects.all(),
        required=False,
        allow_null=True
    )
    next_academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all()
    )
    promotion_date = serializers.DateField(default=timezone.now().date)
    
    def validate_student_ids(self, value):
        """Validate student IDs exist"""
        students = Student.objects.filter(id__in=value)
        if len(students) != len(value):
            raise serializers.ValidationError(
                _('One or more student IDs are invalid.')
            )
        return students


class StudentDocumentUploadSerializer(serializers.Serializer):
    """Serializer for uploading student documents"""
    
    student_id = serializers.UUIDField()
    document_type = serializers.ChoiceField(
        choices=StudentDocument.DOCUMENT_TYPE_CHOICES
    )
    file = serializers.FileField()
    description = serializers.CharField(
        required=False,
        allow_blank=True
    )
    issue_date = serializers.DateField(required=False)
    expiry_date = serializers.DateField(required=False)
    issuing_authority = serializers.CharField(
        required=False,
        allow_blank=True
    )
    
    def validate(self, data):
        """Validate document upload"""
        student_id = data['student_id']
        
        try:
            student = Student.objects.get(id=student_id)
            data['student'] = student
        except Student.DoesNotExist:
            raise serializers.ValidationError({
                'student_id': _('Student does not exist.')
            })
        
        return data


# ============================================================================
# COMPACT SERIALIZERS FOR DROPDOWNS/FILTERS
# ============================================================================

class StudentMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for dropdowns and autocomplete"""
    
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'admission_number', 'roll_number', 'full_name']
        read_only_fields = fields


class StudentAutocompleteSerializer(serializers.ModelSerializer):
    """Serializer for autocomplete search"""
    
    full_name = serializers.CharField(read_only=True)
    current_class_name = serializers.CharField(source='current_class.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'admission_number', 'roll_number', 'full_name',
            'personal_email', 'mobile_primary',
            'current_class_name', 'section_name'
        ]
        read_only_fields = fields