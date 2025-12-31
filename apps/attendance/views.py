import logging
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from apps.core.views import (
    BaseListView, BaseDetailView, BaseCreateView, 
    BaseUpdateView, BaseDeleteView, BaseTemplateView
)
from apps.academics.models import StudentAttendance
from apps.hr.models import StaffAttendance
from apps.hostel.models import HostelAttendance
from apps.transportation.models import TransportAttendance

from apps.attendance.forms import (
    StudentAttendanceForm, StaffAttendanceForm, 
    HostelAttendanceForm, TransportAttendanceForm
)

from django.http import HttpResponse
from django.views import View
from apps.core.utils.reporting import ReportGenerator

logger = logging.getLogger(__name__)

# ============================================================================
# DASHBOARD
# ============================================================================

class AttendanceDashboardView(BaseTemplateView):
    """Attendance Dashboard"""
    template_name = "attendance/dashboard.html"
    permission_required = 'attendance.view_attendance' # Assuming permission exists or generic
    roles_required = ["admin", "teacher", "principal", "hostel_warden", "transport_manager"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        last_7_days = today - timedelta(days=6)

        # 1. Summary Cards (Today)
        context['student_stats'] = {
            'total': StudentAttendance.objects.filter(date=today).count(),
            'present': StudentAttendance.objects.filter(date=today, status='PRESENT').count(),
            'absent': StudentAttendance.objects.filter(date=today, status='ABSENT').count(),
            'late': StudentAttendance.objects.filter(date=today, status='LATE').count(),
        }
        context['staff_stats'] = {
            'total': StaffAttendance.objects.filter(date=today).count(),
            'present': StaffAttendance.objects.filter(date=today, status='PRESENT').count(),
            'absent': StaffAttendance.objects.filter(date=today, status='ABSENT').count(),
            'late': StaffAttendance.objects.filter(date=today, status='LATE').count(),
        }

        # 2. Charts Data (Last 7 Days Trend)
        trend_data = []
        for i in range(7):
            day = last_7_days + timedelta(days=i)
            s_present = StudentAttendance.objects.filter(date=day, status='PRESENT').count()
            s_absent = StudentAttendance.objects.filter(date=day, status='ABSENT').count()
            
            trend_data.append({
                'date': day.strftime("%d %b"),
                'present': s_present,
                'absent': s_absent
            })
        
        context['trend_data'] = trend_data
        context['recent_attendance'] = StudentAttendance.objects.select_related('student', 'class_name').order_by('-created_at')[:5]

        # 4. Filter Options for Reporting
        from apps.academics.models import SchoolClass, Section, AcademicYear
        from apps.hr.models import Department, Designation
        from apps.hostel.models import Hostel
        from apps.transportation.models import Route
        
        context['classes'] = SchoolClass.objects.filter(is_active=True)
        context['sections'] = Section.objects.filter(is_active=True)
        context['departments'] = Department.objects.all()
        context['designations'] = Designation.objects.all()
        context['hostels'] = Hostel.objects.filter(is_active=True)
        context['routes'] = Route.objects.filter(is_active=True)
        context['academic_years'] = AcademicYear.objects.filter(is_active=True)
        
        context['months'] = [
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
        ]
        context['years'] = range(today.year - 2, today.year + 1)
        context['now'] = timezone.now()

        return context

# ============================================================================
# MARKING MODES (Manual, QR, Face)
# ============================================================================

class MarkAttendanceView(BaseTemplateView):
    """Unified view to select attendance marking mode"""
    template_name = "attendance/mark_selection.html"
    roles_required = ["admin", "teacher", "hostel_warden", "transport_manager"]

class MarkAttendanceManualView(BaseTemplateView):
    """Manual Entry View"""
    template_name = "attendance/mark_manual.html"
    roles_required = ["admin", "teacher", "hostel_warden", "transport_manager"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.academics.models import SchoolClass, Section
        context['classes'] = SchoolClass.objects.filter(is_active=True)
        context['sections'] = Section.objects.filter(is_active=True)
        return context

class MarkAttendanceQRView(BaseTemplateView):
    """QR Code Scanner View"""
    template_name = "attendance/mark_qr.html"
    roles_required = ["admin", "teacher", "hostel_warden", "transport_manager"]

class MarkAttendanceFaceView(BaseTemplateView):
    """Face Recognition View"""
    template_name = "attendance/mark_face.html"
    roles_required = ["admin", "teacher", "hostel_warden", "transport_manager"]

# Staff QR/Face Views
class StaffMarkAttendanceQRView(BaseTemplateView):
    """QR Code Scanning View for Staff"""
    template_name = "attendance/staff_mark_qr.html"
    roles_required = ["admin", "hr_manager", "principal"]

class StaffMarkAttendanceFaceView(BaseTemplateView):
    """Face Recognition View for Staff"""
    template_name = "attendance/staff_mark_face.html"
    roles_required = ["admin", "hr_manager", "principal"]

# Hostel QR/Face Views
class HostelMarkAttendanceQRView(BaseTemplateView):
    """QR Code Scanning View for Hostel"""
    template_name = "attendance/hostel_mark_qr.html"
    roles_required = ["admin", "hostel_warden"]

class HostelMarkAttendanceFaceView(BaseTemplateView):
    """Face Recognition View for Hostel"""
    template_name = "attendance/hostel_mark_face.html"
    roles_required = ["admin", "hostel_warden"]

# Transport QR/Face Views
class TransportMarkAttendanceQRView(BaseTemplateView):
    """QR Code Scanning View for Transport"""
    template_name = "attendance/transport_mark_qr.html"
    roles_required = ["admin", "transport_manager"]

class TransportMarkAttendanceFaceView(BaseTemplateView):
    """Face Recognition View for Transport"""
    template_name = "attendance/transport_mark_face.html"
    roles_required = ["admin", "transport_manager"]

# ============================================================================
# STUDENT ATTENDANCE CURD
# ============================================================================

class StudentAttendanceListView(BaseListView):
    model = StudentAttendance
    template_name = 'attendance/student_attendance_list.html'
    context_object_name = 'attendances'
    ordering = ['-date']
    search_fields = ['student__first_name', 'student__admission_number']
    roles_required = ['admin', 'teacher', 'principal']

class StudentAttendanceDetailView(BaseDetailView):
    model = StudentAttendance
    template_name = 'attendance/student_attendance_detail.html'
    context_object_name = 'attendance'
    roles_required = ['admin', 'teacher', 'principal']

class StudentAttendanceCreateView(BaseCreateView):
    model = StudentAttendance
    form_class = StudentAttendanceForm
    template_name = 'attendance/student_attendance_form.html'
    roles_required = ['admin', 'teacher']
    success_url = reverse_lazy('attendance:student_attendance_list')

    def form_valid(self, form):
        messages.success(self.request, "Student attendance marked successfully.")
        return super().form_valid(form)

class StudentAttendanceUpdateView(BaseUpdateView):
    model = StudentAttendance
    form_class = StudentAttendanceForm
    template_name = 'attendance/student_attendance_form.html'
    roles_required = ['admin', 'teacher']
    success_url = reverse_lazy('attendance:student_attendance_list')

class StudentAttendanceDeleteView(BaseDeleteView):
    model = StudentAttendance
    template_name = 'attendance/student_attendance_confirm_delete.html'
    success_url = reverse_lazy('attendance:student_attendance_list')
    roles_required = ['admin']

# ============================================================================
# STAFF ATTENDANCE CRUD
# ============================================================================

class StaffAttendanceListView(BaseListView):
    model = StaffAttendance
    template_name = 'attendance/staff_attendance_list.html'
    context_object_name = 'attendances'
    ordering = ['-date']
    roles_required = ['admin', 'hr_manager', 'principal']

class StaffAttendanceDetailView(BaseDetailView):
    model = StaffAttendance
    template_name = 'attendance/staff_attendance_detail.html'
    context_object_name = 'attendance'
    roles_required = ['admin', 'hr_manager', 'principal']

class StaffAttendanceCreateView(BaseCreateView):
    model = StaffAttendance
    form_class = StaffAttendanceForm
    template_name = 'attendance/staff_attendance_form.html'
    roles_required = ['admin', 'hr_manager']
    success_url = reverse_lazy('attendance:staff_attendance_list')

class StaffAttendanceUpdateView(BaseUpdateView):
    model = StaffAttendance
    form_class = StaffAttendanceForm
    template_name = 'attendance/staff_attendance_form.html'
    roles_required = ['admin', 'hr_manager']
    success_url = reverse_lazy('attendance:staff_attendance_list')

class StaffAttendanceDeleteView(BaseDeleteView):
    model = StaffAttendance
    template_name = 'attendance/staff_attendance_confirm_delete.html'
    success_url = reverse_lazy('attendance:staff_attendance_list')
    roles_required = ['admin', 'hr_manager']

# ============================================================================
# HOSTEL ATTENDANCE CRUD
# ============================================================================

class HostelAttendanceListView(BaseListView):
    model = HostelAttendance
    template_name = 'attendance/hostel_attendance_list.html'
    context_object_name = 'attendances'
    ordering = ['-date']
    roles_required = ['admin', 'hostel_warden']

class HostelAttendanceDetailView(BaseDetailView):
    model = HostelAttendance
    template_name = 'attendance/hostel_attendance_detail.html'
    context_object_name = 'attendance'
    roles_required = ['admin', 'hostel_warden']

class HostelAttendanceCreateView(BaseCreateView):
    model = HostelAttendance
    form_class = HostelAttendanceForm
    template_name = 'attendance/hostel_attendance_form.html'
    roles_required = ['admin', 'hostel_warden']
    success_url = reverse_lazy('attendance:hostel_attendance_list')

class HostelAttendanceUpdateView(BaseUpdateView):
    model = HostelAttendance
    form_class = HostelAttendanceForm
    template_name = 'attendance/hostel_attendance_form.html'
    roles_required = ['admin', 'hostel_warden']
    success_url = reverse_lazy('attendance:hostel_attendance_list')

class HostelAttendanceDeleteView(BaseDeleteView):
    model = HostelAttendance
    template_name = 'attendance/hostel_attendance_confirm_delete.html'
    success_url = reverse_lazy('attendance:hostel_attendance_list')
    roles_required = ['admin', 'hostel_warden']

# ============================================================================
# TRANSPORT ATTENDANCE CRUD
# ============================================================================

class TransportAttendanceListView(BaseListView):
    model = TransportAttendance
    template_name = 'attendance/transport_attendance_list.html'
    context_object_name = 'attendances'
    ordering = ['-date']
    roles_required = ['admin', 'transport_manager']

class TransportAttendanceDetailView(BaseDetailView):
    model = TransportAttendance
    template_name = 'attendance/transport_attendance_detail.html'
    context_object_name = 'attendance'
    roles_required = ['admin', 'transport_manager']

class TransportAttendanceCreateView(BaseCreateView):
    model = TransportAttendance
    form_class = TransportAttendanceForm
    template_name = 'attendance/transport_attendance_form.html'
    roles_required = ['admin', 'transport_manager']
    success_url = reverse_lazy('attendance:transport_attendance_list')

class TransportAttendanceUpdateView(BaseUpdateView):
    model = TransportAttendance
    form_class = TransportAttendanceForm
    template_name = 'attendance/transport_attendance_form.html'
    roles_required = ['admin', 'transport_manager']
    success_url = reverse_lazy('attendance:transport_attendance_list')

class TransportAttendanceDeleteView(BaseDeleteView):
    model = TransportAttendance
    template_name = 'attendance/transport_attendance_confirm_delete.html'
    success_url = reverse_lazy('attendance:transport_attendance_list')
    roles_required = ['admin', 'transport_manager']


# ============================================================================
# REPORTING
# ============================================================================

class AttendanceReportExportView(View):
    """
    Universal export view for Student, Staff, Hostel, and Transport attendance.
    """
    def get(self, request):
        source = request.GET.get('source', 'student')
        format_type = request.GET.get('format', 'pdf')
        month = request.GET.get('month')
        year = request.GET.get('year')
        
        # Base Querysets
        if source == 'student':
            class_id = request.GET.get('class_id')
            section_id = request.GET.get('section_id')
            queryset = StudentAttendance.objects.all()
            if class_id: queryset = queryset.filter(class_name_id=class_id)
            if section_id: queryset = queryset.filter(section_id=section_id)
            if month and year: queryset = queryset.filter(date__month=month, date__year=year)
            
            data = queryset.values('student__first_name', 'student__last_name', 'student__admission_number', 'class_name__name', 'section__name', 'date', 'status')
            columns = ['First Name', 'Last Name', 'Admission No', 'Class', 'Section', 'Date', 'Status']
            title = "Student Attendance Report"
            
        elif source == 'staff':
            dept_id = request.GET.get('dept_id')
            desig_id = request.GET.get('desig_id')
            queryset = StaffAttendance.objects.all()
            if dept_id: queryset = queryset.filter(staff__department_id=dept_id)
            if desig_id: queryset = queryset.filter(staff__designation_id=desig_id)
            if month and year: queryset = queryset.filter(date__month=month, date__year=year)
            
            data = queryset.values('staff__user__first_name', 'staff__user__last_name', 'staff__employee_id', 'staff__department__name', 'date', 'status', 'check_in', 'check_out')
            columns = ['First Name', 'Last Name', 'Employee ID', 'Department', 'Date', 'Status', 'In', 'Out']
            title = "Staff Attendance Report"

        elif source == 'hostel':
            hostel_id = request.GET.get('hostel_id')
            queryset = HostelAttendance.objects.all()
            if hostel_id: queryset = queryset.filter(student__hostel_allocation__hostel_id=hostel_id)
            if month and year: queryset = queryset.filter(date__month=month, date__year=year)
            
            data = queryset.values('student__first_name', 'student__last_name', 'student__hostel_allocation__hostel__name', 'date', 'status')
            columns = ['First Name', 'Last Name', 'Hostel', 'Date', 'Status']
            title = "Hostel Attendance Report"

        elif source == 'transport':
            route_id = request.GET.get('route_id')
            trip_type = request.GET.get('trip_type')
            queryset = TransportAttendance.objects.all()
            if route_id: queryset = queryset.filter(student__transport_allocation__route_id=route_id)
            if trip_type: queryset = queryset.filter(trip_type=trip_type)
            if month and year: queryset = queryset.filter(date__month=month, date__year=year)
            
            data = queryset.values('student__first_name', 'student__last_name', 'trip_type', 'date', 'status')
            columns = ['First Name', 'Last Name', 'Trip', 'Date', 'Status']
            title = "Transport Attendance Report"
        
        else:
            return HttpResponse("Invalid source", status=400)

        # Generate report
        filename = f"{source}_attendance_{timezone.now().strftime('%Y%m%d')}"
        
        if format_type == 'csv':
            return ReportGenerator.generate_csv(list(data), columns, filename=filename)
        elif format_type == 'excel':
            return ReportGenerator.generate_excel(list(data), columns, filename=filename)
        else:
            return ReportGenerator.generate_pdf(list(data), columns, filename=filename, title=title)