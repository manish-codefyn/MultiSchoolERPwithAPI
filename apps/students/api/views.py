# In apps/students/api/views.py

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q, Avg, Sum
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
import logging

# Base API Views
from apps.core.api.views import (
    BaseListAPIView, BaseRetrieveAPIView, BaseCreateAPIView,
    BaseUpdateAPIView, BaseDestroyAPIView, BaseListCreateAPIView,
    BaseRetrieveUpdateAPIView, BaseRetrieveUpdateDestroyAPIView,
    BulkOperationAPIView, ExportAPIView, DashboardAPIView
)
from rest_framework.generics import ListAPIView
# Models
from apps.students.models import (
    Student, Guardian, StudentAddress, StudentDocument,
    StudentMedicalInfo, StudentAcademicHistory, StudentIdentification
)
from apps.academics.models import SchoolClass, Section, AcademicYear
from apps.exams.models import ExamResult
from apps.academics.models import StudentAttendance
from apps.finance.models import Invoice, Payment

# Serializers
from apps.students.api.serializers import (
    StudentListSerializer, StudentDetailSerializer,
    StudentCreateSerializer, StudentUpdateSerializer,
    GuardianSerializer, StudentAddressSerializer,
    StudentDocumentSerializer, StudentMedicalInfoSerializer,
    StudentAcademicHistorySerializer, StudentIdentificationSerializer,
    StudentBulkCreateSerializer, StudentImportSerializer,
    StudentExportSerializer, StudentStatisticsSerializer,
    StudentPromotionSerializer, StudentDocumentUploadSerializer,
    StudentMinimalSerializer
)

# Services
from apps.core.services.audit_service import AuditService
from apps.core.services.export_service import ExportService
from apps.core.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


# ============================================================================
# STUDENT CRUD VIEWS
# ============================================================================
class StudentListAPIView(BaseListAPIView):
    """
    List all students with filtering, searching, ordering and summary
    """
    serializer_class = StudentListSerializer
    model = Student
    roles_required = ['admin', 'teacher', 'hr_manager', 'principal', 'vice_principal']

    search_fields = [
        'first_name',
        'last_name',
        'middle_name',
        'admission_number',
        'roll_number',
        'reg_no',
        'personal_email',
        'institutional_email',
    ]

    filterset_fields = {
        'current_class': ['exact'],
        'section': ['exact'],
        'status': ['exact', 'in'],
        'gender': ['exact'],
        'category': ['exact', 'in'],
        'admission_type': ['exact'],
        'academic_year': ['exact'],
        'is_physically_challenged': ['exact'],
        'is_minority': ['exact'],
        'fee_category': ['exact'],
        'current_semester': ['exact', 'gte', 'lte'],
        'enrollment_date': ['gte', 'lte', 'exact'],
        'date_of_birth': ['gte', 'lte', 'exact'],
    }

    ordering_fields = [
        'first_name',
        'last_name',
        'admission_number',
        'roll_number',
        'enrollment_date',
        'date_of_birth',
        'created_at',
        'updated_at',
    ]

    ordering = ['first_name', 'last_name']

    # ----------------------------------------
    # Custom filters
    # ----------------------------------------
    def apply_custom_filters(self, queryset):
        request = self.request

        # Admission year
        admission_year = request.query_params.get("admission_year")
        if admission_year and admission_year.isdigit():
            queryset = queryset.filter(enrollment_date__year=int(admission_year))

        # Age filtering
        today = timezone.now().date()

        min_age = request.query_params.get("min_age")
        max_age = request.query_params.get("max_age")

        if min_age and min_age.isdigit():
            max_birth_date = today.replace(year=today.year - int(min_age))
            queryset = queryset.filter(date_of_birth__lte=max_birth_date)

        if max_age and max_age.isdigit():
            min_birth_date = today.replace(year=today.year - int(max_age) - 1)
            queryset = queryset.filter(date_of_birth__gte=min_birth_date)

        # CGPA filtering
        min_cgpa = request.query_params.get("min_cgpa")
        max_cgpa = request.query_params.get("max_cgpa")

        if min_cgpa:
            queryset = queryset.filter(cumulative_grade_point__gte=float(min_cgpa))

        if max_cgpa:
            queryset = queryset.filter(cumulative_grade_point__lte=float(max_cgpa))

        # Outstanding fees
        has_outstanding_fees = request.query_params.get("has_outstanding_fees")
        if has_outstanding_fees:
            from apps.finance.models import Invoice

            if has_outstanding_fees.lower() == "true":
                student_ids = Invoice.objects.filter(
                    status__in=["PENDING", "OVERDUE"]
                ).values_list("student_id", flat=True)

                queryset = queryset.filter(id__in=student_ids)

        return queryset

    # ----------------------------------------
    # Custom response with summary
    # ----------------------------------------
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # Calculate summary on the filtered queryset
        # Note: We must re-apply filters to get accurate counts for the summary
        # effectively doing two queries, but necessary for accurate summary of "what calls matched"
        queryset = self.filter_queryset(self.get_queryset())

        summary = {
            "total_students": queryset.count(),
            "active_students": queryset.filter(status="ACTIVE").count(),
            "inactive_students": queryset.filter(status="INACTIVE").count(),
            "alumni_students": queryset.filter(status="ALUMNI").count(),
            "by_gender": {
                "male": queryset.filter(gender="M").count(),
                "female": queryset.filter(gender="F").count(),
                "other": queryset.filter(gender="O").count(),
            },
        }

        # Pagination-safe response handling
        if isinstance(response.data, dict):
            # If already paginated (has 'results'), just add summary
            # If somehow not paginated (unlikely with BaseListAPIView), wrap it
            if "results" in response.data:
                response.data["summary"] = summary
            else:
                 # Should not happen with StandardResultsSetPagination but for safety
                response.data = {
                    "results": response.data,
                    "summary": summary,
                }
        
        return response

class StudentCreateAPIView(BaseCreateAPIView):
    """
    Create a new student with all related data
    """
    model = Student
    serializer_class = StudentCreateSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR']
    
    def perform_create(self, serializer):
        """Override to add custom logic"""
        # Add tenant from request
        serializer.validated_data['tenant'] = self.tenant
        serializer.validated_data['created_by'] = self.request.user
        
        # Generate admission number if not provided
        if not serializer.validated_data.get('admission_number'):
            # This will be handled in the model's save method
            pass
        
        # Save the instance
        student = serializer.save()
        
        # Send notification
        try:
            NotificationService.send_student_registration_notification(
                student=student,
                user=self.request.user
            )
        except Exception as e:
            logger.error(f"Failed to send registration notification: {e}")
        
        return student
    
    def create(self, request, *args, **kwargs):
        """Handle student creation with audit logging"""
        response = super().create(request, *args, **kwargs)
        
        # Additional audit logging
        if response.status_code == status.HTTP_201_CREATED:
            student_id = response.data.get('id')
            if student_id:
                try:
                    student = Student.objects.get(id=student_id)
                    AuditService.create_audit_entry(
                        action='STUDENT_CREATED',
                        resource_type='Student',
                        user=request.user,
                        request=request,
                        instance=student,
                        extra_data={
                            'created_via': 'api',
                            'student_admission_number': student.admission_number,
                            'with_guardians': student.guardians.count(),
                            'with_addresses': student.addresses.count()
                        }
                    )
                except Student.DoesNotExist:
                    pass
        
        return response


class StudentDetailAPIView(BaseRetrieveAPIView):
    """
    Retrieve a single student with all related data
    """
    model = Student
    serializer_class = StudentDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve with additional context"""
        instance = self.get_object()
        
        # Add query params to context for dynamic data
        context = self.get_serializer_context()
        
        # Add attendance period if specified
        if 'attendance_start_date' in request.query_params:
            context['attendance_start_date'] = request.query_params.get('attendance_start_date')
        if 'attendance_end_date' in request.query_params:
            context['attendance_end_date'] = request.query_params.get('attendance_end_date')
        
        serializer = self.get_serializer(instance, context=context)
        return Response(serializer.data)


class StudentUpdateAPIView(BaseUpdateAPIView):
    """
    Update an existing student
    """
    model = Student
    serializer_class = StudentUpdateSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR', 'TEACHER']
    
    def get_serializer_context(self):
        """Add extra context to serializer"""
        context = super().get_serializer_context()
        context['update_mode'] = True
        return context
    
    def perform_update(self, serializer):
        """Handle update with tracking"""
        # Store old data for audit
        old_instance = self.get_object()
        
        # Update the instance
        instance = serializer.save()
        
        # Track what was changed
        changed_fields = []
        for field in serializer.validated_data:
            old_value = getattr(old_instance, field, None)
            new_value = getattr(instance, field, None)
            if old_value != new_value:
                changed_fields.append(field)
        
        # Log detailed audit
        if changed_fields:
            AuditService.log_update(
                user=self.request.user,
                instance=instance,
                old_instance=old_instance,
                request=self.request,
                extra_data={
                    'changed_fields': changed_fields,
                    'update_via': 'api'
                }
            )
        
        return instance


class StudentDeleteAPIView(BaseDestroyAPIView):
    """
    Delete a student (soft delete)
    """
    model = Student
    serializer_class = StudentDetailSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']
    require_delete_reason = True
    
    def perform_destroy(self, instance):
        """Override to handle soft delete with notifications"""
        delete_reason = self.request.data.get('deletion_reason', '')
        delete_category = self.request.data.get('deletion_category', '')
        
        # Perform soft delete
        instance.delete(
            user=self.request.user,
            reason=delete_reason,
            category=delete_category
        )
        
        # Send notification
        try:
            NotificationService.send_student_deletion_notification(
                student=instance,
                deleted_by=self.request.user,
                reason=delete_reason
            )
        except Exception as e:
            logger.error(f"Failed to send deletion notification: {e}")


class StudentRetrieveUpdateDestroyAPIView(BaseRetrieveUpdateDestroyAPIView):
    """
    Combined view for retrieve, update, and delete operations
    """
    model = Student
    serializer_class = StudentDetailSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR', 'TEACHER']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on method"""
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return StudentUpdateSerializer
        return StudentDetailSerializer


# ============================================================================
# RELATED MODEL VIEWS
# ============================================================================

class StudentGuardianListCreateAPIView(BaseListCreateAPIView):
    """
    List and create guardians for a student
    """
    model = Guardian
    serializer_class = GuardianSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR', 'TEACHER']
    
    def get_queryset(self):
        """Filter guardians by student"""
        student_id = self.kwargs.get('student_id')
        return Guardian.objects.filter(
            student_id=student_id,
            student__tenant=self.tenant
        )
    
    def perform_create(self, serializer):
        """Assign student to guardian"""
        student_id = self.kwargs.get('student_id')
        student = get_object_or_404(
            Student,
            id=student_id,
            tenant=self.tenant
        )
        serializer.save(student=student)


class StudentGuardianDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific guardian
    """
    model = Guardian
    serializer_class = GuardianSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR', 'TEACHER']
    
    def get_queryset(self):
        """Filter by tenant"""
        return Guardian.objects.filter(student__tenant=self.tenant)


class StudentAddressListCreateAPIView(BaseListCreateAPIView):
    """
    List and create addresses for a student
    """
    model = StudentAddress
    serializer_class = StudentAddressSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR', 'TEACHER']
    
    def get_queryset(self):
        """Filter addresses by student"""
        student_id = self.kwargs.get('student_id')
        return StudentAddress.objects.filter(
            student_id=student_id,
            student__tenant=self.tenant
        )
    
    def perform_create(self, serializer):
        """Assign student to address"""
        student_id = self.kwargs.get('student_id')
        student = get_object_or_404(
            Student,
            id=student_id,
            tenant=self.tenant
        )
        serializer.save(student=student)


class StudentAddressDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific address
    """
    model = StudentAddress
    serializer_class = StudentAddressSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR', 'TEACHER']
    
    def get_queryset(self):
        """Filter by tenant"""
        return StudentAddress.objects.filter(student__tenant=self.tenant)


class StudentMedicalInfoRetrieveUpdateAPIView(BaseRetrieveUpdateAPIView):
    """
    Retrieve or update medical info for a student
    """
    model = StudentMedicalInfo
    serializer_class = StudentMedicalInfoSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR']

    def get_object(self):
        student_id = self.kwargs.get('student_id')
        # Ensure student exists and belongs to tenant
        student = get_object_or_404(Student, id=student_id, tenant=self.tenant)
        
        # Get or create medical info
        obj, created = StudentMedicalInfo.objects.get_or_create(
            student=student, 
            defaults={'tenant': self.tenant}
        )
        return obj


class StudentIdentificationRetrieveUpdateAPIView(BaseRetrieveUpdateAPIView):
    """
    Retrieve or update identification info for a student
    """
    model = StudentIdentification
    serializer_class = StudentIdentificationSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR']
    
    def get_object(self):
        student_id = self.kwargs.get('student_id')
        student = get_object_or_404(Student, id=student_id, tenant=self.tenant)
        
        obj, created = StudentIdentification.objects.get_or_create(
            student=student,
            defaults={'tenant': self.tenant}
        )
        return obj


class StudentAcademicHistoryListCreateAPIView(BaseListCreateAPIView):
    """
    List and create academic history for a student
    """
    model = StudentAcademicHistory
    serializer_class = StudentAcademicHistorySerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR', 'TEACHER']
    
    def get_queryset(self):
        """Filter by student"""
        student_id = self.kwargs.get('student_id')
        return StudentAcademicHistory.objects.filter(
            student_id=student_id,
            student__tenant=self.tenant
        )
    
    def perform_create(self, serializer):
        """Assign student"""
        student_id = self.kwargs.get('student_id')
        student = get_object_or_404(
            Student,
            id=student_id,
            tenant=self.tenant
        )
        serializer.save(student=student)


class StudentAcademicHistoryDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific academic history record
    """
    model = StudentAcademicHistory
    serializer_class = StudentAcademicHistorySerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR', 'TEACHER']
    
    def get_queryset(self):
        """Filter by tenant"""
        return StudentAcademicHistory.objects.filter(student__tenant=self.tenant)


class StudentDocumentListCreateAPIView(BaseListCreateAPIView):
    """
    List and create documents for a student
    """
    model = StudentDocument
    serializer_class = StudentDocumentSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR', 'TEACHER']
    
    def get_queryset(self):
        """Filter documents by student"""
        student_id = self.kwargs.get('student_id')
        return StudentDocument.objects.filter(
            student_id=student_id,
            student__tenant=self.tenant,
            is_current=True
        )
    
    def perform_create(self, serializer):
        """Assign student to document"""
        student_id = self.kwargs.get('student_id')
        student = get_object_or_404(
            Student,
            id=student_id,
            tenant=self.tenant
        )
        serializer.save(student=student)


class StudentDocumentDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific document
    """
    model = StudentDocument
    serializer_class = StudentDocumentSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR', 'TEACHER']
    
    def get_queryset(self):
        """Filter by tenant"""
        return StudentDocument.objects.filter(student__tenant=self.tenant)


class StudentDocumentVerifyAPIView(BaseUpdateAPIView):
    """
    Verify a document
    """
    model = StudentDocument
    serializer_class = StudentDocumentSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR']

    def post(self, request, *args, **kwargs):
        """Verify a document"""
        document = self.get_object()
        
        if document.is_verified:
            return Response({'error': 'Document already verified'}, status=400)
        
        notes = request.data.get('notes', '')
        document.verify_document(request.user, notes)
        
        return Response({'status': 'verified'})


class StudentDocumentRejectAPIView(BaseUpdateAPIView):
    """
    Reject a document
    """
    model = StudentDocument
    serializer_class = StudentDocumentSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR']

    def post(self, request, *args, **kwargs):
        """Reject a document"""
        document = self.get_object()
        
        reason = request.data.get('reason', '')
        if not reason:
            return Response({'error': 'Rejection reason is required'}, status=400)
        
        document.reject_document(request.user, reason)
        
        return Response({'status': 'rejected'})


# ============================================================================
# SPECIALIZED VIEWS
# ============================================================================

class StudentIDCardAPIView(BaseRetrieveAPIView):
    """
    Generate Student ID Card
    """
    model = Student
    serializer_class = StudentDetailSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR', 'TEACHER', 'STUDENT']
    
    def get(self, request, *args, **kwargs):
        """Generate ID card PDF"""
        student = self.get_object()
        
        # Check if student has photo - REMOVED to allow placeholder
        # if not student.get_photo():
        #     return Response(
        #         {'error': 'Student photo is required for ID card'},
        #         status=400
        #     )
        
        # Generate ID card (example using reportlab)
        try:
            from apps.students.services.idcard_service import IDCardService
            id_card_service = IDCardService(student)
            
            # Get ID card as PNG (Frontend expects image for preview and printing wrapping)
            png_buffer = id_card_service.generate_card_image()
            png_content = png_buffer.getvalue()
            
            # Return PNG response
            response = HttpResponse(png_content, content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="ID_Card_{student.admission_number}.png"'
            return response
            
        except ImportError:
            # Fallback to HTML response if PDF generation fails
            context = {
                'student': student,
                'institution_name': self.tenant.name if hasattr(self.tenant, 'name') else 'School',
                'issue_date': timezone.now().date(),
                'valid_until': timezone.now().date().replace(year=timezone.now().year + 1)
            }
            return Response(context)
        except Exception as e:
            logger.error(f"ID Card generation error: {e}")
            return Response(
                {'error': 'Failed to generate ID card'},
                status=500
            )


class StudentPromoteAPIView(BaseUpdateAPIView):
    """
    Promote student to next class/semester
    """
    model = Student
    serializer_class = StudentUpdateSerializer
    roles_required = ['ADMIN', 'PRINCIPAL']
    
    def post(self, request, *args, **kwargs):
        """Promote student"""
        student = self.get_object()
        
        serializer = StudentPromotionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        try:
            with transaction.atomic():
                # Get promotion data
                target_class = serializer.validated_data['target_class']
                next_academic_year = serializer.validated_data['next_academic_year']
                target_section = serializer.validated_data.get('target_section')
                promotion_date = serializer.validated_data['promotion_date']
                
                # Store old data
                old_class = student.current_class
                old_section = student.section
                old_academic_year = student.academic_year
                
                # Update student
                student.current_class = target_class
                student.section = target_section
                student.academic_year = next_academic_year
                
                # Increment semester if applicable
                if hasattr(student, 'current_semester'):
                    student.current_semester += 1
                
                student.save()
                
                # Create academic history record
                StudentAcademicHistory.objects.create(
                    student=student,
                    academic_year=old_academic_year,
                    class_name=old_class,
                    section=old_section,
                    roll_number=student.roll_number,
                    result='PASS',
                    promoted=True
                )
                
                # Log audit
                AuditService.create_audit_entry(
                    action='STUDENT_PROMOTED',
                    resource_type='Student',
                    user=request.user,
                    request=request,
                    instance=student,
                    extra_data={
                        'old_class': str(old_class),
                        'new_class': str(target_class),
                        'old_academic_year': str(old_academic_year),
                        'new_academic_year': str(next_academic_year),
                        'promotion_date': promotion_date.isoformat()
                    }
                )
                
                # Send notification
                try:
                    NotificationService.send_student_promotion_notification(
                        student=student,
                        promoted_by=request.user,
                        old_class=old_class,
                        new_class=target_class
                    )
                except Exception as e:
                    logger.error(f"Failed to send promotion notification: {e}")
                
                return Response({
                    'status': 'promoted',
                    'student': StudentDetailSerializer(student).data,
                    'old_class': str(old_class),
                    'new_class': str(target_class)
                })
                
        except Exception as e:
            logger.error(f"Promotion error: {e}")
            return Response({'error': str(e)}, status=500)


class StudentReportCardAPIView(BaseRetrieveAPIView):
    """
    Get student report card data
    """
    model = Student
    serializer_class = StudentDetailSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'TEACHER', 'STUDENT', 'PARENT']
    
    def get(self, request, *args, **kwargs):
        """Get comprehensive report card"""
        student = self.get_object()
        
        # Check permissions for student/parent
        if request.user.role in ['STUDENT', 'PARENT']:
            if request.user.role == 'STUDENT' and student.user != request.user:
                raise PermissionDenied("You can only view your own report card.")
            if request.user.role == 'PARENT':
                # Check if user is a guardian of this student
                if not Guardian.objects.filter(
                    student=student,
                    email=request.user.email
                ).exists():
                    raise PermissionDenied("You can only view your ward's report card.")
        
        # Get academic year
        academic_year = request.query_params.get('academic_year')
        if not academic_year:
            academic_year = student.academic_year
        
        # Gather attendance data
        attendance_summary = self.get_attendance_summary(student, academic_year)
        
        # Gather exam results
        exam_results = self.get_exam_results(student, academic_year)
        
        # Calculate overall performance
        overall_performance = self.calculate_overall_performance(exam_results)
        
        # Prepare report card data
        report_card = {
            'student': {
                'name': student.full_name,
                'admission_number': student.admission_number,
                'class': str(student.current_class) if student.current_class else '',
                'section': str(student.section) if student.section else '',
                'roll_number': student.roll_number,
            },
            'academic_year': str(academic_year),
            'report_date': timezone.now().isoformat(),
            'attendance_summary': attendance_summary,
            'exam_results': exam_results,
            'overall_performance': overall_performance,
            'teacher_remarks': self.get_teacher_remarks(student, academic_year),
            'principal_remarks': '',
            'is_passed': overall_performance.get('result') == 'PASS'
        }
        
        return Response(report_card)
    
    def get_attendance_summary(self, student, academic_year):
        """Calculate attendance summary"""
        from apps.academics.models import StudentAttendance
        
        attendances = StudentAttendance.objects.filter(
            student=student,
            academic_year=academic_year
        )
        
        total_days = attendances.count()
        if total_days == 0:
            return {
                'total_days': 0,
                'present_days': 0,
                'absent_days': 0,
                'leave_days': 0,
                'percentage': 0.0
            }
        
        present_days = attendances.filter(status='PRESENT').count()
        absent_days = attendances.filter(status='ABSENT').count()
        leave_days = attendances.filter(status='LEAVE').count()
        
        percentage = (present_days / total_days) * 100 if total_days > 0 else 0
        
        return {
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'leave_days': leave_days,
            'percentage': round(percentage, 2)
        }
    
    def get_exam_results(self, student, academic_year):
        """Get exam results for academic year"""
        from apps.exams.models import ExamResult
        
        results = ExamResult.objects.filter(
            student=student,
            exam__academic_year=academic_year
        ).select_related('exam', 'subject')
        
        exam_results = []
        for result in results:
            exam_results.append({
                'exam_name': result.exam.name,
                'subject': result.subject.name if result.subject else '',
                'marks_obtained': float(result.marks_obtained) if result.marks_obtained else 0,
                'total_marks': float(result.total_marks) if result.total_marks else 100,
                'percentage': float(result.percentage) if result.percentage else 0,
                'grade': result.grade,
                'grade_point': float(result.grade_point) if result.grade_point else 0,
                'result_status': result.result_status,
                'rank': result.rank
            })
        
        return exam_results
    
    def calculate_overall_performance(self, exam_results):
        """Calculate overall performance from exam results"""
        if not exam_results:
            return {
                'total_subjects': 0,
                'passed_subjects': 0,
                'failed_subjects': 0,
                'total_marks': 0,
                'obtained_marks': 0,
                'percentage': 0.0,
                'cgpa': 0.0,
                'result': 'FAIL'
            }
        
        total_subjects = len(exam_results)
        passed_subjects = sum(1 for r in exam_results if r['result_status'] == 'PASS')
        failed_subjects = total_subjects - passed_subjects
        
        total_marks = sum(r['total_marks'] for r in exam_results)
        obtained_marks = sum(r['marks_obtained'] for r in exam_results)
        percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
        
        # Calculate CGPA (average of grade points)
        grade_points = [r['grade_point'] for r in exam_results if r['grade_point']]
        cgpa = sum(grade_points) / len(grade_points) if grade_points else 0
        
        result = 'PASS' if failed_subjects == 0 else 'FAIL'
        
        return {
            'total_subjects': total_subjects,
            'passed_subjects': passed_subjects,
            'failed_subjects': failed_subjects,
            'total_marks': total_marks,
            'obtained_marks': obtained_marks,
            'percentage': round(percentage, 2),
            'cgpa': round(cgpa, 2),
            'result': result
        }
    
    def get_teacher_remarks(self, student, academic_year):
        """Get teacher remarks for student"""
        # This would typically come from a TeacherRemarks model
        return "Good performance. Needs improvement in Mathematics."


class StudentBulkActionAPIView(BulkOperationAPIView):
    """
    Bulk operations on students
    """
    model = Student
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR']
    
    def perform_bulk_action(self, action, selected_ids):
        """Perform bulk action on selected students"""
        queryset = self.get_queryset().filter(id__in=selected_ids)
        
        if action == 'activate':
            queryset.update(status='ACTIVE', is_active=True)
            return f'Activated {queryset.count()} students'
        
        elif action == 'deactivate':
            queryset.update(status='INACTIVE', is_active=False)
            return f'Deactivated {queryset.count()} students'
        
        elif action == 'archive':
            queryset.update(status='ALUMNI')
            return f'Archived {queryset.count()} students'
        
        elif action == 'promote':
            # Bulk promotion requires additional data
            target_class_id = self.request.data.get('target_class_id')
            if not target_class_id:
                raise ValidationError({'target_class_id': 'This field is required for promotion.'})
            
            try:
                target_class = SchoolClass.objects.get(id=target_class_id, tenant=self.tenant)
                count = 0
                for student in queryset:
                    student.current_class = target_class
                    if hasattr(student, 'current_semester'):
                        student.current_semester += 1
                    student.save()
                    count += 1
                return f'Promoted {count} students to {target_class.name}'
            except SchoolClass.DoesNotExist:
                raise ValidationError({'target_class_id': 'Class not found.'})
        
        elif action == 'update_category':
            category = self.request.data.get('category')
            if not category:
                raise ValidationError({'category': 'This field is required.'})
            
            queryset.update(category=category)
            return f'Updated category for {queryset.count()} students'
        
        elif action == 'update_fee_category':
            fee_category = self.request.data.get('fee_category')
            if not fee_category:
                raise ValidationError({'fee_category': 'This field is required.'})
            
            queryset.update(fee_category=fee_category)
            return f'Updated fee category for {queryset.count()} students'
        
        elif action == 'generate_credentials':
            count = 0
            for student in queryset:
                if not student.user:
                    try:
                        student.create_user_account()
                        count += 1
                    except Exception as e:
                        logger.error(f"Failed to create user account for student {student.id}: {e}")
            return f'Generated credentials for {count} students'
        
        else:
            raise ValidationError({'action': f'Invalid action: {action}'})


class StudentExportAPIView(ExportAPIView):
    """
    Export students data
    """
    model = Student
    serializer_class = StudentExportSerializer
    
    def get_export_filename(self):
        """Get export filename"""
        return f"students_export_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
    
    def get_export_headers(self):
        """Get CSV headers"""
        return [
            'Admission Number',
            'Roll Number',
            'Full Name',
            'First Name',
            'Middle Name',
            'Last Name',
            'Date of Birth',
            'Age',
            'Gender',
            'Blood Group',
            'Personal Email',
            'Institutional Email',
            'Primary Mobile',
            'Secondary Mobile',
            'Current Class',
            'Section',
            'Admission Type',
            'Enrollment Date',
            'Category',
            'Religion',
            'Is Minority',
            'Physically Challenged',
            'Status',
            'Guardian Name',
            'Guardian Phone',
            'Address',
            'Created Date'
        ]
    
    def get_export_row(self, obj):
        """Get data row for export"""
        # Get primary guardian
        primary_guardian = obj.guardians.filter(is_primary=True).first()
        guardian_name = primary_guardian.full_name if primary_guardian else ''
        guardian_phone = primary_guardian.phone_primary if primary_guardian else ''
        
        # Get current address
        current_address = obj.addresses.filter(is_current=True).first()
        address = current_address.formatted_address if current_address else ''
        
        return [
            obj.admission_number,
            obj.roll_number,
            obj.full_name,
            obj.first_name,
            obj.middle_name,
            obj.last_name,
            obj.date_of_birth.strftime('%Y-%m-%d') if obj.date_of_birth else '',
            obj.age,
            obj.get_gender_display(),
            obj.blood_group,
            obj.personal_email,
            obj.institutional_email,
            obj.mobile_primary,
            obj.mobile_secondary,
            obj.current_class.name if obj.current_class else '',
            obj.section.name if obj.section else '',
            obj.get_admission_type_display(),
            obj.enrollment_date.strftime('%Y-%m-%d') if obj.enrollment_date else '',
            obj.get_category_display(),
            obj.get_religion_display() if obj.religion else '',
            'Yes' if obj.is_minority else 'No',
            'Yes' if obj.is_physically_challenged else 'No',
            obj.get_status_display(),
            guardian_name,
            guardian_phone,
            address,
            obj.created_at.strftime('%Y-%m-%d %H:%M:%S') if obj.created_at else ''
        ]
    
    def get_queryset(self):
        """Get filtered queryset for export"""
        queryset = super().get_queryset()
        
        # Apply additional filters from request
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        class_filter = self.request.query_params.get('class_id')
        if class_filter:
            queryset = queryset.filter(current_class_id=class_filter)
        
        return queryset


# ============================================================================
# ADDITIONAL STUDENT VIEWS
# ============================================================================

class StudentStatisticsAPIView(DashboardAPIView):
    """
    Get comprehensive student statistics
    """
    model = Student
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR']
    
    def get(self, request, *args, **kwargs):
        """Get student statistics"""
        
        # Get basic counts
        total_students = Student.objects.filter(tenant=self.tenant).count()
        active_students = Student.objects.filter(tenant=self.tenant, status='ACTIVE').count()
        inactive_students = Student.objects.filter(tenant=self.tenant, status='INACTIVE').count()
        alumni_students = Student.objects.filter(tenant=self.tenant, status='ALUMNI').count()
        suspended_students = Student.objects.filter(tenant=self.tenant, status='SUSPENDED').count()
        
        # Gender distribution
        male_students = Student.objects.filter(tenant=self.tenant, gender='M').count()
        female_students = Student.objects.filter(tenant=self.tenant, gender='F').count()
        other_gender_students = Student.objects.filter(tenant=self.tenant, gender='O').count()
        
        # Class distribution
        class_distribution = {}
        classes = SchoolClass.objects.filter(tenant=self.tenant)
        for cls in classes:
            count = Student.objects.filter(
                tenant=self.tenant,
                current_class=cls,
                status='ACTIVE'
            ).count()
            if count > 0:
                class_distribution[cls.name] = count
        
        # Category distribution
        category_distribution = {}
        categories = dict(Student.CATEGORY_CHOICES)
        for category_code, category_name in categories.items():
            count = Student.objects.filter(
                tenant=self.tenant,
                category=category_code,
                status='ACTIVE'
            ).count()
            if count > 0:
                category_distribution[category_name] = count
        
        # Monthly enrollment trend (last 12 months)
        monthly_enrollment = {}
        today = timezone.now()
        for i in range(11, -1, -1):
            month = today.replace(day=1) - timezone.timedelta(days=30*i)
            month_key = month.strftime('%b %Y')
            count = Student.objects.filter(
                tenant=self.tenant,
                enrollment_date__year=month.year,
                enrollment_date__month=month.month
            ).count()
            monthly_enrollment[month_key] = count
        
        # Average age
        avg_age = Student.objects.filter(
            tenant=self.tenant,
            status='ACTIVE'
        ).aggregate(avg_age=Avg('age'))['avg_age'] or 0
        
        # Document compliance
        students_with_docs = 0
        students_without_docs = 0
        
        # This is a simplified check - you might need more complex logic
        for student in Student.objects.filter(tenant=self.tenant, status='ACTIVE'):
            if student.has_required_documents():
                students_with_docs += 1
            else:
                students_without_docs += 1
        
        statistics = {
            'total_students': total_students,
            'active_students': active_students,
            'inactive_students': inactive_students,
            'alumni_students': alumni_students,
            'suspended_students': suspended_students,
            'male_students': male_students,
            'female_students': female_students,
            'other_gender_students': other_gender_students,
            'class_distribution': class_distribution,
            'category_distribution': category_distribution,
            'monthly_enrollment': monthly_enrollment,
            'average_age': round(avg_age, 1) if avg_age else 0,
            'with_required_documents': students_with_docs,
            'without_required_documents': students_without_docs,
            'document_compliance_rate': round(
                (students_with_docs / active_students * 100) if active_students > 0 else 0, 1
            )
        }
        
        serializer = StudentStatisticsSerializer(statistics)
        return Response(serializer.data)


class StudentBulkCreateAPIView(BaseCreateAPIView):
    """
    Bulk create students from CSV/Excel
    """
    serializer_class = StudentBulkCreateSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR']
    
    def create(self, request, *args, **kwargs):
        """Handle bulk creation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = serializer.save()
        
        # Log audit
        AuditService.create_audit_entry(
            action='BULK_STUDENT_CREATE',
            resource_type='Student',
            user=request.user,
            request=request,
            extra_data={
                'count': result['created'],
                'via': 'api'
            }
        )
        
        return Response(result, status=status.HTTP_201_CREATED)


class StudentImportAPIView(BaseCreateAPIView):
    """
    Import students from CSV/Excel file
    """
    serializer_class = StudentImportSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR']
    
    def create(self, request, *args, **kwargs):
        """Handle file import"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uploaded_file = serializer.validated_data['file']
        create_user_accounts = serializer.validated_data.get('create_user_accounts', False)
        send_welcome_emails = serializer.validated_data.get('send_welcome_emails', False)
        
        try:
            # Import service
            from apps.students.services.import_service import StudentImportService
            
            import_service = StudentImportService(
                tenant=self.tenant,
                created_by=request.user
            )
            
            result = import_service.import_from_file(
                uploaded_file,
                create_user_accounts=create_user_accounts,
                send_welcome_emails=send_welcome_emails
            )
            
            # Log audit
            AuditService.create_audit_entry(
                action='STUDENT_IMPORT',
                resource_type='Student',
                user=request.user,
                request=request,
                extra_data={
                    'file_name': uploaded_file.name,
                    'created': result.get('created', 0),
                    'updated': result.get('updated', 0),
                    'failed': result.get('failed', 0),
                    'errors': result.get('errors', [])
                }
            )
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"Student import error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudentSearchAPIView(BaseListAPIView):
    """
    Advanced search for students
    """
    model = Student
    serializer_class = StudentListSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR', 'TEACHER']
    
    def get_queryset(self):
        """Apply advanced search filters"""
        queryset = super().get_queryset()
        
        # Get search parameters
        search_params = self.request.query_params
        
        # Name search (supports partial matching)
        name = search_params.get('name')
        if name:
            queryset = queryset.filter(
                Q(first_name__icontains=name) |
                Q(last_name__icontains=name) |
                Q(middle_name__icontains=name) |
                Q(full_name__icontains=name)
            )
        
        # Contact search
        email = search_params.get('email')
        if email:
            queryset = queryset.filter(
                Q(personal_email__icontains=email) |
                Q(institutional_email__icontains=email)
            )
        
        phone = search_params.get('phone')
        if phone:
            queryset = queryset.filter(
                Q(mobile_primary__icontains=phone) |
                Q(mobile_secondary__icontains=phone)
            )
        
        # Guardian search
        guardian_name = search_params.get('guardian_name')
        if guardian_name:
            queryset = queryset.filter(
                guardians__full_name__icontains=guardian_name
            ).distinct()
        
        # Address search
        address = search_params.get('address')
        if address:
            queryset = queryset.filter(
                addresses__address_line1__icontains=address
            ).distinct()
        
        # Multiple status filter
        statuses = search_params.getlist('status')
        if statuses:
            queryset = queryset.filter(status__in=statuses)
        
        # Date range filters
        enrollment_date_from = search_params.get('enrollment_date_from')
        enrollment_date_to = search_params.get('enrollment_date_to')
        if enrollment_date_from:
            queryset = queryset.filter(enrollment_date__gte=enrollment_date_from)
        if enrollment_date_to:
            queryset = queryset.filter(enrollment_date__lte=enrollment_date_to)
        
        # Birth date range
        birth_date_from = search_params.get('birth_date_from')
        birth_date_to = search_params.get('birth_date_to')
        if birth_date_from:
            queryset = queryset.filter(date_of_birth__gte=birth_date_from)
        if birth_date_to:
            queryset = queryset.filter(date_of_birth__lte=birth_date_to)
        
        return queryset


class StudentAutocompleteAPIView(BaseListAPIView):
    """
    Autocomplete search for students
    """
    model = Student
    serializer_class = StudentMinimalSerializer
    pagination_class = None
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR', 'TEACHER']
    
    def get_queryset(self):
        """Get queryset for autocomplete"""
        queryset = super().get_queryset()
        
        search_term = self.request.query_params.get('q', '')
        if search_term:
            queryset = queryset.filter(
                Q(admission_number__icontains=search_term) |
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(full_name__icontains=search_term) |
                Q(personal_email__icontains=search_term) |
                Q(mobile_primary__icontains=search_term)
            )
        
        return queryset[:10]  # Limit to 10 results


class StudentDashboardAPIView(BaseRetrieveAPIView):
    """
    Student dashboard with summary information
    """
    model = Student
    serializer_class = StudentDetailSerializer
    roles_required = ['ADMIN', 'PRINCIPAL', 'REGISTRAR', 'TEACHER', 'STUDENT']
    
    def get(self, request, *args, **kwargs):
        """Get student dashboard data"""
        student = self.get_object()
        
        # Check permissions
        if request.user.role == 'STUDENT' and student.user != request.user:
            raise PermissionDenied("You can only view your own dashboard.")
        
        if request.user.role == 'PARENT':
            # Check if user is a guardian
            if not Guardian.objects.filter(
                student=student,
                email=request.user.email
            ).exists():
                raise PermissionDenied("You can only view your ward's dashboard.")
        
        # Gather dashboard data
        dashboard_data = {
            'student': StudentDetailSerializer(student).data,
            'attendance_summary': self.get_attendance_summary(student),
            'academic_summary': self.get_academic_summary(student),
            'fee_summary': self.get_fee_summary(student),
            'upcoming_events': self.get_upcoming_events(student),
            'recent_announcements': self.get_recent_announcements(student),
            'quick_links': self.get_quick_links(student)
        }
        
        return Response(dashboard_data)
    
    def get_attendance_summary(self, student):
        """Get attendance summary for current month"""
        from apps.academics.models import StudentAttendance
        
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        attendances = StudentAttendance.objects.filter(
            student=student,
            date__gte=month_start,
            date__lte=today
        )
        
        total = attendances.count()
        present = attendances.filter(status='PRESENT').count()
        percentage = (present / total * 100) if total > 0 else 0
        
        return {
            'month': today.strftime('%B %Y'),
            'total_days': total,
            'present_days': present,
            'percentage': round(percentage, 1)
        }
    
    def get_academic_summary(self, student):
        """Get academic summary"""
        from apps.exams.models import ExamResult
        
        latest_result = ExamResult.objects.filter(
            student=student
        ).order_by('-created_at').first()
        
        if latest_result:
            return {
                'latest_exam': latest_result.exam.name,
                'marks': float(latest_result.marks_obtained) if latest_result.marks_obtained else 0,
                'total_marks': float(latest_result.total_marks) if latest_result.total_marks else 100,
                'percentage': float(latest_result.percentage) if latest_result.percentage else 0,
                'grade': latest_result.grade,
                'rank': latest_result.rank
            }
        
        return {}
    
    def get_fee_summary(self, student):
        """Get fee summary"""
        from apps.finance.models import Invoice
        
        current_invoices = Invoice.objects.filter(
            student=student,
            due_date__gte=timezone.now().date()
        )
        
        total_due = sum(invoice.amount_due for invoice in current_invoices)
        paid_amount = sum(invoice.paid_amount for invoice in current_invoices)
        
        return {
            'total_due': float(total_due),
            'paid_amount': float(paid_amount),
            'pending_invoices': current_invoices.filter(status='PENDING').count(),
            'overdue_invoices': current_invoices.filter(status='OVERDUE').count()
        }
    
    def get_upcoming_events(self, student):
        """Get upcoming events for student"""
        from apps.events.models import Event
        
        events = Event.objects.filter(
            tenant=self.tenant,
            start_date__gte=timezone.now().date()
        )[:5]
        
        return [
            {
                'title': event.title,
                'start_date': event.start_date.isoformat(),
                'end_date': event.end_date.isoformat() if event.end_date else None,
                'venue': event.venue
            }
            for event in events
        ]
    
    def get_recent_announcements(self, student):
        """Get recent announcements"""
        from apps.core.models import Announcement
        
        announcements = Announcement.objects.filter(
            tenant=self.tenant,
            target_audience__contains=['STUDENT']
        ).order_by('-created_at')[:5]
        
        return [
            {
                'title': announcement.title,
                'content': announcement.content[:100] + '...' if len(announcement.content) > 100 else announcement.content,
                'created_at': announcement.created_at.isoformat()
            }
            for announcement in announcements
        ]
    
    def get_quick_links(self, student):
        """Get quick links for student dashboard"""
        return [
            {'title': 'View Timetable', 'url': f'/timetable/student/{student.id}'},
            {'title': 'Download ID Card', 'url': f'/students/{student.id}/id-card'},
            {'title': 'View Report Card', 'url': f'/students/{student.id}/report-card'},
            {'title': 'Pay Fees Online', 'url': f'/finance/pay/{student.id}'},
            {'title': 'Library Portal', 'url': '/library'},
            {'title': 'Submit Assignment', 'url': '/academics/assignments'}
        ]