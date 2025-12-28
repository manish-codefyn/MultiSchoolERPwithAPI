import logging
from django.db import transaction
from django.shortcuts import redirect
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
        # We need a list of dates and counts for Present/Absent
        trend_data = []
        for i in range(7):
            day = last_7_days + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            
            s_present = StudentAttendance.objects.filter(date=day, status='PRESENT').count()
            s_absent = StudentAttendance.objects.filter(date=day, status='ABSENT').count()
            
            trend_data.append({
                'date': day.strftime("%d %b"),
                'present': s_present,
                'absent': s_absent
            })
        
        context['trend_data'] = trend_data

        # 3. Recent Activity (Last 5 records across types)
        # Just fetching latest 5 students for now as a sample
        context['recent_attendance'] = StudentAttendance.objects.select_related('student', 'class_name').order_by('-created_at')[:5]

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