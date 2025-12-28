from django import forms
from apps.core.forms import TenantAwareModelForm
from apps.academics.models import StudentAttendance
from apps.hr.models import StaffAttendance
from apps.hostel.models import HostelAttendance
from apps.transportation.models import TransportAttendance

class StudentAttendanceForm(TenantAwareModelForm):
    class Meta:
        model = StudentAttendance
        fields = ['student', 'date', 'status', 'class_name', 'section', 'remarks', 'marked_by']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class StaffAttendanceForm(TenantAwareModelForm):
    class Meta:
        model = StaffAttendance
        fields = ['staff', 'date', 'status', 'remarks', 'marked_by']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class HostelAttendanceForm(TenantAwareModelForm):
    class Meta:
        model = HostelAttendance
        fields = ['student', 'date', 'status', 'remarks', 'marked_by']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'check_in_time': forms.TimeInput(attrs={'type': 'time'}),
            'check_out_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class TransportAttendanceForm(TenantAwareModelForm):
    class Meta:
        model = TransportAttendance
        fields = ['student', 'date', 'trip_type', 'status', 'actual_time', 'remarks', 'marked_by']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'actual_time': forms.TimeInput(attrs={'type': 'time'}),
        }