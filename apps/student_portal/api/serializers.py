from rest_framework import serializers
from django.utils import timezone
from apps.core.api.serializers import TenantAwareSerializer
from apps.students.models import Student, StudentDocument
from apps.finance.models import Invoice, Payment
from apps.assignments.models import Assignment, Submission
from apps.academics.models import TimeTable, Subject, StudentAttendance
from apps.hostel.models import Hostel, Room, HostelAllocation, HostelAttendance
from apps.exams.models import Exam, ExamResult, SubjectResult, ExamSubject
from apps.communications.models import MessageThread, Message


# ============================================================================
# STUDENT SERIALIZERS
# ============================================================================

class StudentProfileSerializer(TenantAwareSerializer):
    """Serializer for student's own profile"""
    
    id = serializers.UUIDField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    
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
    
    photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'admission_number', 'roll_number',
            'first_name', 'middle_name', 'last_name', 'full_name',
            'date_of_birth', 'age', 'gender', 'blood_group',
            'personal_email', 'mobile_primary',
            'current_class', 'current_class_name',
            'section', 'section_name',
            'photo_url', 'status',
            'created_at'
        ]
        read_only_fields = fields
    
    def get_photo_url(self, obj):
        """Get student photo URL"""
        photo = obj.get_photo()
        if photo and photo.file:
            request = self.context.get('request')
            photo_url = photo.file.url
            if request:
                return request.build_absolute_uri(photo_url)
            return photo_url
        return None


# ============================================================================
# FINANCE SERIALIZERS
# ============================================================================

class InvoiceListSerializer(TenantAwareSerializer):
    """Serializer for listing student invoices"""
    
    id = serializers.UUIDField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'issue_date', 'due_date',
            'total_amount', 'paid_amount', 'due_amount',
            'status', 'status_display', 'print_url', 'download_url'
        ]
        read_only_fields = fields

    print_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    def get_print_url(self, obj):
        request = self.context.get('request')
        if request:
            from django.urls import reverse
            path = reverse('student_portal:print_invoice', kwargs={'pk': obj.pk})
            return request.build_absolute_uri(path)
        return None

    def get_download_url(self, obj):
        request = self.context.get('request')
        if request:
            from django.urls import reverse
            path = reverse('student_portal:download_invoice', kwargs={'pk': obj.pk})
            return request.build_absolute_uri(path)
        return None


class InvoiceDetailSerializer(InvoiceListSerializer):
    """Detailed invoice serializer"""
    
    items = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()
    
    class Meta(InvoiceListSerializer.Meta):
        fields = InvoiceListSerializer.Meta.fields + [
            'items', 'payments', 'notes', 'created_at'
        ]
    
    def get_items(self, obj):
        return [{
            'id': str(item.id),
            'fee_type_name': item.fee_structure.get_fee_type_display() if item.fee_structure else "Other",
            'amount': item.amount,
            'description': item.description,
        } for item in obj.items.all()]
    
    def get_payments(self, obj):
        return [{
            'id': str(p.id),
            'amount': str(p.amount),
            'payment_date': p.payment_date,
            'payment_method': p.payment_method,
            'status': p.status
        } for p in obj.payments.all()]


# ============================================================================
# ASSIGNMENT SERIALIZERS
# ============================================================================

class SubjectSerializer(TenantAwareSerializer):
    """Subject serializer for assignments"""
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code']
        read_only_fields = fields


class AssignmentListSerializer(TenantAwareSerializer):
    """Serializer for listing assignments"""
    
    id = serializers.UUIDField(read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='class_name.name', read_only=True)
    type_display = serializers.CharField(source='get_assignment_type_display', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    submission_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'assignment_type', 'type_display',
            'subject', 'subject_name', 'class_name',
            'assigned_date', 'due_date', 'max_marks',
            'is_overdue', 'submission_status',
            'attachment', 'created_at'
        ]
        read_only_fields = fields

    attachment = serializers.SerializerMethodField()

    def get_attachment(self, obj):
        if obj.attachment:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.attachment.url)
            return obj.attachment.url
        return None
    
    def get_submission_status(self, obj):
        """Check if current student has submitted"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            student = Student.objects.get(user=request.user)
            submission = Submission.objects.filter(
                assignment=obj, student=student
            ).first()
            
            if submission:
                return {
                    'submitted': True,
                    'status': submission.status,
                    'marks_obtained': str(submission.marks_obtained) if submission.marks_obtained else None,
                    'submitted_at': submission.submitted_at
                }
            return {'submitted': False}
        except Student.DoesNotExist:
            return None


class AssignmentDetailSerializer(AssignmentListSerializer):
    """Detailed assignment serializer"""
    
    attachment_url = serializers.SerializerMethodField()
    my_submission = serializers.SerializerMethodField()
    
    class Meta(AssignmentListSerializer.Meta):
        fields = AssignmentListSerializer.Meta.fields + [
            'attachment_url', 'my_submission'
        ]
    
    def get_attachment_url(self, obj):
        if obj.attachment:
            return obj.attachment.url
        return None
    
    def get_my_submission(self, obj):
        """Get current student's submission details"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            student = Student.objects.get(user=request.user)
            submission = Submission.objects.filter(
                assignment=obj, student=student
            ).first()
            
            if submission:
                return {
                    'id': str(submission.id),
                    'submission_text': submission.submission_text,
                    'submission_file': submission.submission_file.url if submission.submission_file else None,
                    'submitted_at': submission.submitted_at,
                    'status': submission.status,
                    'marks_obtained': str(submission.marks_obtained) if submission.marks_obtained else None,
                    'teacher_remarks': submission.teacher_remarks
                }
            return None
        except Student.DoesNotExist:
            return None


class SubmissionCreateSerializer(TenantAwareSerializer):
    """Serializer for creating assignment submissions"""
    
    assignment = serializers.PrimaryKeyRelatedField(queryset=Assignment.objects.all())
    submission_text = serializers.CharField(required=False, allow_blank=True)
    submission_file = serializers.FileField(required=False)
    
    class Meta:
        model = Submission
        fields = ['assignment', 'submission_text', 'submission_file']
    
    def validate(self, data):
        """Validate submission"""
        request = self.context.get('request')
        
        # Get student
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            raise serializers.ValidationError("Student profile not found")
        
        # Check if already submitted
        if Submission.objects.filter(
            assignment=data['assignment'],
            student=student
        ).exists():
            raise serializers.ValidationError("You have already submitted this assignment")
        
        # Check if assignment is for student's class
        assignment = data['assignment']
        if assignment.class_name != student.current_class:
            raise serializers.ValidationError("This assignment is not for your class")
        
        data['student'] = student
        return data
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['tenant'] = request.tenant
        return super().create(validated_data)


# ============================================================================
# TIMETABLE SERIALIZERS
# ============================================================================

class TimetableSerializer(TenantAwareSerializer):
    """Serializer for timetable entries"""
    
    subject_name = serializers.CharField(source='subject.subject.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    day_display = serializers.CharField(source='get_day_display', read_only=True)
    room_name = serializers.CharField(source='room', read_only=True)
    
    class Meta:
        model = TimeTable
        fields = [
            'id', 'day', 'day_display',
            'period_number', 'start_time', 'end_time',
            'subject', 'subject_name',
            'teacher_name', 'room_name'
        ]
        read_only_fields = fields
    
    def get_teacher_name(self, obj):
        if obj.teacher:
            return obj.teacher.get_full_name()
        return None


# ============================================================================
# COMMUNICATION SERIALIZERS
# ============================================================================

class MessageSerializer(TenantAwareSerializer):
    """Serializer for messages"""
    
    sent_at = serializers.DateTimeField(source='created_at', read_only=True)
    text = serializers.CharField(source='body', read_only=True)
    is_me = serializers.SerializerMethodField()
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'text', 'sender', 'sender_name',
            'is_me', 'sent_at'
        ]
        read_only_fields = fields
    
    def get_sender_name(self, obj):
        if obj.sender:
            return obj.sender.get_full_name()
        return "System"
    
    def get_is_me(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender_id == request.user.id
        return False


class MessageThreadSerializer(TenantAwareSerializer):
    """Serializer for message threads"""
    
    other_participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MessageThread
        fields = [
            'id', 'other_participant', 'last_message',
            'unread_count', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_other_participant(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return "System"
        other = obj.participants.exclude(id=request.user.id).first()
        if not other:
            # If only one participant (the user), or no others found
            other = obj.participants.first()
        return other.get_full_name() if other else "System"

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        return last_msg.body if last_msg else None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        from apps.communications.models import MessageRecipient
        return MessageRecipient.objects.filter(
            message__thread=obj, 
            recipient=request.user, 
            is_read=False
        ).count()


class MessageThreadDetailSerializer(MessageThreadSerializer):
    """Detailed thread with messages"""
    
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta(MessageThreadSerializer.Meta):
        fields = MessageThreadSerializer.Meta.fields + ['messages']


class NotificationSerializer(TenantAwareSerializer):
    """Serializer for notifications"""
    
    class Meta:
        from apps.communications.models import Notification
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type',
            'is_read', 'created_at'
        ]
        read_only_fields = fields


# ============================================================================
# ATTENDANCE SERIALIZERS
# ============================================================================

class StudentAttendanceSerializer(TenantAwareSerializer):
    """Serializer for student attendance records"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    session_display = serializers.CharField(source='get_session_display', read_only=True)
    
    class Meta:
        model = StudentAttendance
        fields = [
            'id', 'date', 'status', 'status_display',
            'session', 'session_display', 'remarks'
        ]
        read_only_fields = fields

# ============================================================================
# HOSTEL SERIALIZERS
# ============================================================================

class HostelSerializer(TenantAwareSerializer):
    """Serializer for hostel details"""
    type_display = serializers.CharField(source='get_hostel_type_display', read_only=True)
    
    class Meta:
        model = Hostel
        fields = ['id', 'name', 'code', 'hostel_type', 'type_display', 'address']
        read_only_fields = fields

class RoomSerializer(TenantAwareSerializer):
    """Serializer for room details"""
    type_display = serializers.CharField(source='get_room_type_display', read_only=True)
    
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'floor', 'room_type', 'type_display', 'capacity']
        read_only_fields = fields

class HostelAllocationSerializer(TenantAwareSerializer):
    """Serializer for student hostel allocation"""
    hostel_details = HostelSerializer(source='hostel', read_only=True)
    room_details = RoomSerializer(source='room', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = HostelAllocation
        fields = [
            'id', 'hostel_details', 'room_details',
            'allocation_date', 'status', 'status_display',
            'is_active', 'bed_number'
        ]
        read_only_fields = fields

class HostelAttendanceSerializer(TenantAwareSerializer):
    """Serializer for hostel attendance"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = HostelAttendance
        fields = ['id', 'date', 'status', 'status_display', 'remarks']
        read_only_fields = fields

# ============================================================================
# EXAM & RESULT SERIALIZERS
# ============================================================================

class ExamListSerializer(TenantAwareSerializer):
    """Serializer for exam listing"""
    exam_type_name = serializers.CharField(source='exam_type.name', read_only=True)
    class_name_display = serializers.CharField(source='class_name.name', read_only=True)
    academic_year_display = serializers.CharField(source='academic_year.name', read_only=True)
    
    class Meta:
        model = Exam
        fields = [
            'id', 'name', 'exam_type_name', 'class_name_display',
            'academic_year_display', 'start_date', 'end_date', 'status', 'is_published'
        ]
        read_only_fields = fields

class SubjectResultSerializer(TenantAwareSerializer):
    """Serializer for individual subject marks"""
    subject_name = serializers.CharField(source='exam_subject.subject.name', read_only=True)
    max_marks = serializers.DecimalField(source='exam_subject.max_marks', max_digits=5, decimal_places=2, read_only=True)
    pass_marks = serializers.DecimalField(source='exam_subject.pass_marks', max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = SubjectResult
        fields = [
            'id', 'subject_name', 'theory_marks', 'practical_marks', 
            'total_marks', 'max_marks', 'pass_marks', 'is_absent', 'grade_point'
        ]
        read_only_fields = fields

class ExamResultSerializer(TenantAwareSerializer):
    """Serializer for full exam results"""
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    exam_type = serializers.CharField(source='exam.exam_type.name', read_only=True)
    subject_results = SubjectResultSerializer(source='subject_results', many=True, read_only=True)
    status_display = serializers.CharField(source='get_result_status_display', read_only=True)
    overall_grade_display = serializers.CharField(source='overall_grade.name', read_only=True, default='-')
    
    class Meta:
        model = ExamResult
        fields = [
            'id', 'exam_name', 'exam_type', 'total_marks', 'obtained_marks',
            'percentage', 'result_status', 'status_display', 'overall_grade_display',
            'rank', 'is_published', 'subject_results'
        ]
        read_only_fields = fields

# ============================================================================
# DASHBOARD SERIALIZERS
# ============================================================================

class DashboardSerializer(serializers.Serializer):
    """Dashboard summary serializer"""
    
    student = StudentProfileSerializer(read_only=True)
    pending_fees = serializers.DecimalField(max_digits=10, decimal_places=2)
    pending_invoice_count = serializers.IntegerField()
    upcoming_assignments = AssignmentListSerializer(many=True, read_only=True)
    attendance_percentage = serializers.FloatField(required=False)
