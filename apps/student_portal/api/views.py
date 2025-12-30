from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Sum

from apps.core.api.views import (
    BaseAPIView, BaseListAPIView, BaseRetrieveAPIView,
    BaseCreateAPIView, StandardResultsSetPagination
)
from apps.students.models import Student
from apps.finance.models import Invoice
from apps.assignments.models import Assignment, Submission
from apps.academics.models import TimeTable
from apps.communications.models import MessageThread, Message

from .serializers import (
    StudentProfileSerializer,
    InvoiceListSerializer, InvoiceDetailSerializer,
    AssignmentListSerializer, AssignmentDetailSerializer, SubmissionCreateSerializer,
    TimetableSerializer,
    MessageThreadSerializer, MessageThreadDetailSerializer, MessageSerializer,
    NotificationSerializer, StudentAttendanceSerializer,
    HostelAllocationSerializer, HostelAttendanceSerializer, HostelSerializer,
    ExamListSerializer, ExamResultSerializer,
    DashboardSerializer
)
from apps.academics.models import StudentAttendance
from apps.hostel.models import HostelAllocation, HostelAttendance, Hostel
from apps.exams.models import Exam, ExamResult
from apps.communications.models import MessageThread, Message, Notification


# ============================================================================
# STUDENT PORTAL MIXIN
# ============================================================================

class StudentPortalMixin:
    """Mixin to get current student from authenticated user"""
    
    def get_student(self):
        """Get student profile for current user"""
        if not self.request.user.is_authenticated:
            return None
        try:
            return Student.objects.get(user=self.request.user, tenant=self.request.tenant)
        except Student.DoesNotExist:
            return None


# ============================================================================
# DASHBOARD API
# ============================================================================

class StudentDashboardAPIView(StudentPortalMixin, BaseAPIView):
    """Get student dashboard data"""
    
    def get(self, request, *args, **kwargs):
        student = self.get_student()
        if not student:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get pending fees
        unpaid_invoices = Invoice.objects.filter(
            student=student,
            status__in=['ISSUED', 'PARTIALLY_PAID', 'OVERDUE']
        )
        pending_fees = unpaid_invoices.aggregate(Sum('due_amount'))['due_amount__sum'] or 0
        
        # Get upcoming assignments
        upcoming_assignments = Assignment.objects.filter(
            class_name=student.current_class,
            due_date__gte=timezone.now(),
            status='PUBLISHED'
        ).exclude(
            submissions__student=student
        ).order_by('due_date')[:5]
        
        data = {
            'student': StudentProfileSerializer(student, context={'request': request}).data,
            'pending_fees': pending_fees,
            'pending_invoice_count': unpaid_invoices.count(),
            'upcoming_assignments': AssignmentListSerializer(
                upcoming_assignments, many=True, context={'request': request}
            ).data
        }
        
        return Response(data)


# ============================================================================
# PROFILE API
# ============================================================================

class StudentProfileAPIView(StudentPortalMixin, BaseAPIView):
    """Get current student's profile"""
    
    def get(self, request, *args, **kwargs):
        student = self.get_student()
        if not student:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = StudentProfileSerializer(student, context={'request': request})
        return Response(serializer.data)


# ============================================================================
# INVOICE APIs
# ============================================================================

class InvoiceListAPIView(StudentPortalMixin, BaseListAPIView):
    """List student's invoices"""
    
    serializer_class = InvoiceListSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        student = self.get_student()
        if not student:
            return Invoice.objects.none()
        return Invoice.objects.filter(student=student).order_by('-issue_date')


class InvoiceDetailAPIView(StudentPortalMixin, BaseRetrieveAPIView):
    """Get invoice details"""
    
    serializer_class = InvoiceDetailSerializer
    
    def get_queryset(self):
        student = self.get_student()
        if not student:
            return Invoice.objects.none()
        return Invoice.objects.filter(student=student)


# ============================================================================
# ASSIGNMENT APIs
# ============================================================================

class AssignmentListAPIView(StudentPortalMixin, BaseListAPIView):
    """List assignments for student's class"""
    
    serializer_class = AssignmentListSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['assignment_type', 'subject']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'created_at']
    ordering = ['-due_date']
    
    def get_queryset(self):
        student = self.get_student()
        if not student:
            return Assignment.objects.none()
        
        return Assignment.objects.filter(
            class_name=student.current_class,
            status='PUBLISHED'
        ).filter(
            Q(section__isnull=True) | Q(section=student.section)
        ).select_related('subject', 'class_name')
    
    def list(self, request, *args, **kwargs):
        """Custom list to categorize assignments"""
        student = self.get_student()
        if not student:
            return Response({'error': 'Student not found'}, status=404)
        
        queryset = self.get_queryset()
        now = timezone.now()
        
        # Get submitted assignment IDs
        submitted_ids = list(Submission.objects.filter(
            student=student
        ).values_list('assignment_id', flat=True))
        
        # Categorize
        pending = queryset.filter(due_date__gte=now).exclude(id__in=submitted_ids)
        overdue = queryset.filter(due_date__lt=now).exclude(id__in=submitted_ids)
        submitted = queryset.filter(id__in=submitted_ids)
        
        return Response({
            'pending': AssignmentListSerializer(pending, many=True, context={'request': request}).data,
            'overdue': AssignmentListSerializer(overdue, many=True, context={'request': request}).data,
            'submitted': AssignmentListSerializer(submitted, many=True, context={'request': request}).data,
            'counts': {
                'pending': pending.count(),
                'overdue': overdue.count(),
                'submitted': submitted.count()
            }
        })


class AssignmentDetailAPIView(StudentPortalMixin, BaseRetrieveAPIView):
    """Get assignment details"""
    
    serializer_class = AssignmentDetailSerializer
    
    def get_queryset(self):
        student = self.get_student()
        if not student:
            return Assignment.objects.none()
        
        return Assignment.objects.filter(
            class_name=student.current_class,
            status='PUBLISHED'
        ).filter(
            Q(section__isnull=True) | Q(section=student.section)
        )


class AssignmentSubmitAPIView(StudentPortalMixin, BaseCreateAPIView):
    """Submit assignment"""
    
    serializer_class = SubmissionCreateSerializer
    
    def create(self, request, *args, **kwargs):
        # Add assignment ID from URL
        assignment_id = kwargs.get('pk')
        data = request.data.copy()
        data['assignment'] = assignment_id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        submission = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Assignment submitted successfully',
            'submission_id': str(submission.id)
        }, status=status.HTTP_201_CREATED)


# ============================================================================
# TIMETABLE API
# ============================================================================

class TimetableAPIView(StudentPortalMixin, BaseAPIView):
    """Get student's timetable"""
    
    def get(self, request, *args, **kwargs):
        student = self.get_student()
        if not student:
            return Response({'error': 'Student not found'}, status=404)
        
        timetable = TimeTable.objects.filter(
            class_name=student.current_class,
            section=student.section,
            is_active=True
        ).select_related('subject', 'teacher').order_by('day', 'period_number')
        
        # Group by day
        timetable_by_day = {}
        for entry in timetable:
            day = entry.get_day_display()
            if day not in timetable_by_day:
                timetable_by_day[day] = []
            timetable_by_day[day].append(
                TimetableSerializer(entry, context={'request': request}).data
            )
        
        return Response(timetable_by_day)


# ============================================================================
# COMMUNICATION APIs
# ============================================================================

class InboxAPIView(StudentPortalMixin, BaseListAPIView):
    """List message threads"""
    
    serializer_class = MessageThreadSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return MessageThread.objects.none()
        return MessageThread.objects.filter(
            participants=self.request.user
        ).order_by('-updated_at')


class ThreadDetailAPIView(StudentPortalMixin, BaseRetrieveAPIView):
    """Get thread with messages"""
    
    serializer_class = MessageThreadDetailSerializer
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return MessageThread.objects.none()
        return MessageThread.objects.filter(participants=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Mark messages as read for the current user
        from apps.communications.models import MessageRecipient
        MessageRecipient.objects.filter(
            message__thread=instance,
            recipient=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        # Perform audit
        self.perform_audit(instance=instance)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class SendMessageAPIView(StudentPortalMixin, BaseAPIView):
    """Send a message in a thread"""
    
    def post(self, request, pk):
        try:
            thread = MessageThread.objects.get(pk=pk, participants=request.user)
        except MessageThread.DoesNotExist:
            return Response({'error': 'Thread not found'}, status=404)
        
        content = request.data.get('text', request.data.get('content', '')).strip()
        if not content:
            return Response({'error': 'Message content required'}, status=400)
        # Create message
        message = Message.objects.create(
            tenant=request.tenant,
            thread=thread,
            sender=request.user,
            body=content,
            subject=f"Re: {thread.title}"
        )
        
        # Update thread timestamp
        thread.save()  # This updates updated_at
        
        return Response({
            'success': True,
            'message': MessageSerializer(message, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class NotificationListAPIView(StudentPortalMixin, BaseListAPIView):
    """List notifications for the current user"""
    
    serializer_class = NotificationSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Notification.objects.none()
        return Notification.objects.filter(
            recipient=self.request.user,
            is_dismissed=False
        ).order_by('-created_at')


class MarkNotificationReadAPIView(StudentPortalMixin, BaseAPIView):
    """Mark a notification as read"""
    
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(
                pk=pk, 
                recipient=request.user
            )
            notification.is_read = True
            notification.save()
            return Response({'success': True})
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=404)

# ============================================================================
# ATTENDANCE API
# ============================================================================

class AttendanceListAPIView(StudentPortalMixin, BaseListAPIView):
    """List student's attendance records"""
    
    serializer_class = StudentAttendanceSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        student = self.get_student()
        if not student:
            return StudentAttendance.objects.none()
        return StudentAttendance.objects.filter(student=student).order_by('-date')


# ============================================================================
# HOSTEL API
# ============================================================================

class HostelDetailsAPIView(StudentPortalMixin, BaseAPIView):
    """Get current student's hostel allocation and attendance"""
    
    def get(self, request, *args, **kwargs):
        student = self.get_student()
        if not student:
            return Response({'error': 'Student not found'}, status=404)
        
        allocation = HostelAllocation.objects.filter(
            student=student, 
            is_active=True
        ).first()
        
        if not allocation:
            data = {
                'allocation': None,
                'roommates': [],
                'attendance_history': HostelAttendanceSerializer(
                    HostelAttendance.objects.filter(student=student).order_by('-date')[:10],
                    many=True,
                    context={'request': request}
                ).data
            }
            return Response(data)
        
        # Get roommates (other students in the same room)
        roommate_allocations = HostelAllocation.objects.filter(
            room=allocation.room,
            is_active=True
        ).exclude(student=student).select_related('student')
        
        roommates = []
        for a in roommate_allocations:
            photo_url = None
            photo = a.student.get_photo()
            if photo and photo.file:
                photo_url = request.build_absolute_uri(photo.file.url)
            
            roommates.append({
                'id': str(a.student.id),
                'full_name': a.student.full_name,
                'class': a.student.current_class.name if a.student.current_class else None,
                'photo_url': photo_url
            })
        
        # Get recent attendance
        attendance = HostelAttendance.objects.filter(
            student=student
        ).order_by('-date')[:10]
        
        data = {
            'allocation': HostelAllocationSerializer(allocation, context={'request': request}).data,
            'roommates': roommates,
            'attendance_history': HostelAttendanceSerializer(attendance, many=True, context={'request': request}).data
        }
        
        return Response(data)

class HostelListAPIView(StudentPortalMixin, BaseListAPIView):
    """List all available hostels"""
    serializer_class = HostelSerializer
    queryset = Hostel.objects.filter(is_active=True)


# ============================================================================
# EXAMS & RESULTS API
# ============================================================================

class ExamListAPIView(StudentPortalMixin, BaseListAPIView):
    """List exams applicable to the student's class"""
    serializer_class = ExamListSerializer
    
    def get_queryset(self):
        student = self.get_student()
        if not student or not student.current_class:
            return Exam.objects.none()
        
        return Exam.objects.filter(
            class_name=student.current_class,
            is_published=True
        ).order_by('-start_date')

class ExamResultListAPIView(StudentPortalMixin, BaseListAPIView):
    """List results for the current student"""
    serializer_class = ExamResultSerializer
    
    def get_queryset(self):
        student = self.get_student()
        if not student:
            return ExamResult.objects.none()
        
        return ExamResult.objects.filter(
            student=student,
            is_published=True
        ).order_by('-exam__start_date')

class ExamResultDetailAPIView(StudentPortalMixin, BaseAPIView):
    """Get detailed result for a specific exam"""
    
    def get(self, request, pk, *args, **kwargs):
        student = self.get_student()
        if not student:
            return Response({'error': 'Student not found'}, status=404)
        
        try:
            result = ExamResult.objects.get(
                pk=pk,
                student=student,
                is_published=True
            )
            serializer = ExamResultSerializer(result, context={'request': request})
            return Response(serializer.data)
        except ExamResult.DoesNotExist:
            return Response({'error': 'Result not found'}, status=404)
