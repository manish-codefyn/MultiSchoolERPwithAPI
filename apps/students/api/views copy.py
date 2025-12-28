from rest_framework import viewsets
from rest_framework.decorators import action
from apps.core.api.permissions import TenantAccessPermission, RoleRequiredPermission
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions.mixins import TenantAccessMixin
from apps.students.models import *
from .serializers import *

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['teacher', 'student', 'parent', 'admin']

    @action(detail=True, methods=['get'])
    def generate_id_card(self, request, pk=None):
        student = self.get_object()
        from apps.students.idcard import StudentIDCardGenerator
        generator = StudentIDCardGenerator(student)
        return generator.get_id_card_response()

    @action(detail=True, methods=['post'])
    def promote(self, request, pk=None):
        """Promote student to next class"""
        student = self.get_object()
        new_class_id = request.data.get('new_class_id')
        
        if not new_class_id:
            return Response({'error': 'new_class_id is required'}, status=400)
            
        try:
            new_class = SchoolClass.objects.get(id=new_class_id, tenant=request.tenant)
            old_class = student.current_class
            
            student.current_class = new_class
            student.save()
            
            # Audit
            from apps.core.services.audit_service import AuditService
            AuditService.log_update(
                user=request.user,
                instance=student,
                request=request,
                extra_data={
                    'action': 'promotion',
                    'old_class': str(old_class),
                    'new_class': str(new_class)
                }
            )
            return Response({'status': 'promoted', 'new_class': new_class.name})
        except SchoolClass.DoesNotExist:
            return Response({'error': 'Class not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['get'])
    def report_card(self, request, pk=None):
        """Get report card data"""
        student = self.get_object()
        
        # Gather data similar to StudentReportView
        data = {
            'student': StudentSerializer(student).data,
            'academic_year': str(student.academic_year),
            'class': str(student.current_class),
            'report_date': timezone.now().isoformat(),
            # Placeholder for actual grades/attendance
            'attendance_summary': {
                'total_days': 200,
                'present_days': 180,
                'percentage': 90.0
            },
            'exam_results': [] 
            # In a real impl, we'd fetch ExamResultSerializer(student.exam_results.all(), many=True).data
        }
        return Response(data)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export students as CSV/Excel"""
        from apps.students.views import StudentExportView
        # Reuse existing view logic if possible, or reimplement
        # For simplicity, we'll reimplement CSV export here
        import csv
        from django.http import HttpResponse
        
        queryset = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Admission Number', 'Full Name', 'Class', 'Section', 'Status'])
        
        for s in queryset:
            writer.writerow([
                s.admission_number, 
                s.full_name, 
                s.current_class.name if s.current_class else '',
                s.section.name if s.section else '',
                s.status
            ])
            
        return response

    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """Bulk upload students via CSV"""
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'File is required'}, status=400)
            
        try:
            decoded_file = file_obj.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            created_count = 0
            errors = []
            
            for row in reader:
                # Basic mapping logic
                try:
                    # Minimal required fields
                    if 'first_name' not in row or 'last_name' not in row:
                        continue
                        
                    Student.objects.create(
                        tenant=request.tenant,
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        personal_email=row.get('email', ''),
                        admission_number=row.get('admission_number', Student().generate_admission_number()),
                        # Use defaults for others or enhance mapping
                        status='ACTIVE'
                    )
                    created_count += 1
                except Exception as e:
                    errors.append(str(e))
            
            return Response({
                'status': 'success',
                'created': created_count,
                'errors': errors[:5]
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class GuardianViewSet(viewsets.ModelViewSet):
    queryset = Guardian.objects.all()
    serializer_class = GuardianSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['teacher', 'student', 'parent', 'admin']

class StudentAddressViewSet(viewsets.ModelViewSet):
    queryset = StudentAddress.objects.all()
    serializer_class = StudentAddressSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['teacher', 'student', 'parent', 'admin']

class StudentDocumentViewSet(viewsets.ModelViewSet):
    queryset = StudentDocument.objects.all()
    serializer_class = StudentDocumentSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['teacher', 'student', 'parent', 'admin']

class StudentMedicalInfoViewSet(viewsets.ModelViewSet):
    queryset = StudentMedicalInfo.objects.all()
    serializer_class = StudentMedicalInfoSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['teacher', 'student', 'parent', 'admin']

class StudentAcademicHistoryViewSet(viewsets.ModelViewSet):
    queryset = StudentAcademicHistory.objects.all()
    serializer_class = StudentAcademicHistorySerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['teacher', 'student', 'parent', 'admin']

class StudentIdentificationViewSet(viewsets.ModelViewSet):
    queryset = StudentIdentification.objects.all()
    serializer_class = StudentIdentificationSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['teacher', 'student', 'parent', 'admin']

