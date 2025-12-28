import json
import re
from django.urls import reverse_lazy
from django.db.models import Count, Sum, Q
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from apps.core.views import BaseListView, BaseCreateView, BaseUpdateView, BaseDeleteView
from apps.core.utils.tenant import get_current_tenant
from apps.students.models import Student
from .models import Vehicle, Route, RouteStop, TransportAllocation, TransportAttendance, MaintenanceRecord, FuelRecord
from .forms import (
    VehicleForm, RouteForm, RouteStopForm, TransportAllocationForm, 
    TransportAttendanceForm, MaintenanceRecordForm, FuelRecordForm
)

class TransportationDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'transportation/dashboard.html'
    permission_required = 'transportation.view_vehicle'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = get_current_tenant()
        
        # Stats
        context['total_vehicles'] = Vehicle.objects.filter(tenant=tenant, is_active=True).count()
        context['total_routes'] = Route.objects.filter(tenant=tenant, is_active=True).count()
        context['total_allocations'] = TransportAllocation.objects.filter(tenant=tenant, is_active=True).count()
        context['maintenance_vehicles'] = Vehicle.objects.filter(tenant=tenant, under_maintenance=True).count()
        
        # Attendance today
        today = timezone.now().date()
        context['today_attendance'] = TransportAttendance.objects.filter(tenant=tenant, date=today).count()
        
        # Recent Activities
        context['recent_maintenance'] = MaintenanceRecord.objects.filter(tenant=tenant).select_related('vehicle').order_by('-maintenance_date')[:5]
        context['recent_fuel'] = FuelRecord.objects.filter(tenant=tenant).select_related('vehicle').order_by('-date')[:5]
        
        return context

# ==================== VEHICLE ====================

class VehicleListView(BaseListView):
    model = Vehicle
    template_name = 'transportation/vehicle_list.html'
    context_object_name = 'vehicles'
    permission_required = 'transportation.view_vehicle'
    search_fields = ['vehicle_number', 'registration_number', 'make', 'model']
    filter_fields = ['vehicle_type', 'fuel_type', 'status', 'is_active']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add import URL if vehicle import view exists, otherwise leave blank or create one later
        return context

class VehicleCreateView(BaseCreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'transportation/vehicle_form.html'
    permission_required = 'transportation.add_vehicle'
    success_url = reverse_lazy('transportation:vehicle_list')

class VehicleUpdateView(BaseUpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'transportation/vehicle_form.html'
    permission_required = 'transportation.change_vehicle'
    success_url = reverse_lazy('transportation:vehicle_list')

class VehicleDeleteView(BaseDeleteView):
    model = Vehicle
    template_name = 'transportation/confirm_delete.html'
    permission_required = 'transportation.delete_vehicle'
    success_url = reverse_lazy('transportation:vehicle_list')

# ==================== ROUTE ====================

class RouteListView(BaseListView):
    model = Route
    template_name = 'transportation/route_list.html'
    context_object_name = 'routes'
    permission_required = 'transportation.view_route'
    search_fields = ['name', 'code', 'start_point', 'end_point']
    filter_fields = ['is_active']

class RouteCreateView(BaseCreateView):
    model = Route
    form_class = RouteForm
    template_name = 'transportation/route_form.html'
    permission_required = 'transportation.add_route'
    success_url = reverse_lazy('transportation:route_list')

class RouteUpdateView(BaseUpdateView):
    model = Route
    form_class = RouteForm
    template_name = 'transportation/route_form.html'
    permission_required = 'transportation.change_route'
    success_url = reverse_lazy('transportation:route_list')

class RouteDeleteView(BaseDeleteView):
    model = Route
    template_name = 'transportation/confirm_delete.html'
    permission_required = 'transportation.delete_route'
    success_url = reverse_lazy('transportation:route_list')

# ==================== ROUTE STOP ====================

class RouteStopListView(BaseListView):
    model = RouteStop
    template_name = 'transportation/stop_list.html'
    context_object_name = 'stops'
    permission_required = 'transportation.view_routestop'
    search_fields = ['stop_name', 'route__name']

class RouteStopCreateView(BaseCreateView):
    model = RouteStop
    form_class = RouteStopForm
    template_name = 'transportation/stop_form.html'
    permission_required = 'transportation.add_routestop'
    success_url = reverse_lazy('transportation:stop_list')

class RouteStopUpdateView(BaseUpdateView):
    model = RouteStop
    form_class = RouteStopForm
    template_name = 'transportation/stop_form.html'
    permission_required = 'transportation.change_routestop'
    success_url = reverse_lazy('transportation:stop_list')

class RouteStopDeleteView(BaseDeleteView):
    model = RouteStop
    template_name = 'transportation/confirm_delete.html'
    permission_required = 'transportation.delete_routestop'
    success_url = reverse_lazy('transportation:stop_list')

# ==================== ALLOCATION ====================

class TransportAllocationListView(BaseListView):
    model = TransportAllocation
    template_name = 'transportation/allocation_list.html'
    context_object_name = 'allocations'
    permission_required = 'transportation.view_transportallocation'
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_number', 'route__name']
    filter_fields = ['is_active', 'is_fee_paid']

class TransportAllocationCreateView(BaseCreateView):
    model = TransportAllocation
    form_class = TransportAllocationForm
    template_name = 'transportation/allocation_form.html'
    permission_required = 'transportation.add_transportallocation'
    success_url = reverse_lazy('transportation:allocation_list')

class TransportAllocationUpdateView(BaseUpdateView):
    model = TransportAllocation
    form_class = TransportAllocationForm
    template_name = 'transportation/allocation_form.html'
    permission_required = 'transportation.change_transportallocation'
    success_url = reverse_lazy('transportation:allocation_list')

class TransportAllocationDeleteView(BaseDeleteView):
    model = TransportAllocation
    template_name = 'transportation/confirm_delete.html'
    permission_required = 'transportation.delete_transportallocation'
    success_url = reverse_lazy('transportation:allocation_list')


# ==================== ATTENDANCE ====================

class TransportAttendanceListView(BaseListView):
    model = TransportAttendance
    template_name = 'transportation/attendance_list.html'
    context_object_name = 'attendances'
    permission_required = 'transportation.view_transportattendance'
    search_fields = ['student__first_name', 'student__last_name']
    filter_fields = ['status', 'trip_type', 'date']

class TransportAttendanceCreateView(BaseCreateView):
    model = TransportAttendance
    form_class = TransportAttendanceForm
    template_name = 'transportation/attendance_form.html'
    permission_required = 'transportation.add_transportattendance'
    success_url = reverse_lazy('transportation:attendance_list')
    
    def form_valid(self, form):
        form.instance.marked_by = self.request.user
        return super().form_valid(form)

class TransportAttendanceUpdateView(BaseUpdateView):
    model = TransportAttendance
    form_class = TransportAttendanceForm
    template_name = 'transportation/attendance_form.html'
    permission_required = 'transportation.change_transportattendance'
    success_url = reverse_lazy('transportation:attendance_list')

class TransportAttendanceDeleteView(BaseDeleteView):
    model = TransportAttendance
    template_name = 'transportation/confirm_delete.html'
    permission_required = 'transportation.delete_transportattendance'
    success_url = reverse_lazy('transportation:attendance_list')


class TransportQRCodeAttendanceView(LoginRequiredMixin, TemplateView):
    """QR Code based transport attendance marking"""
    template_name = 'transportation/qr_attendance.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        return context

    def post(self, request, *args, **kwargs):
        """Handle QR scan submission"""
        reg_no_input = request.POST.get('reg_no', '').strip()
        trip_type = request.POST.get('trip_type', 'PICKUP')
        
        if not reg_no_input:
            return JsonResponse({'status': 'error', 'message': 'No input provided'})
            
        tenant = request.tenant
        student = None
        
        # Pattern: ADM followed by anything until whitespace, newline or end
        admission_match = re.search(r'(ADM-\\d{4}-[A-Za-z0-9_]+-\\d+)', reg_no_input, re.IGNORECASE)
        
        if admission_match:
            search_term = admission_match.group(1).strip()
            student = Student.objects.filter(
                tenant=tenant,
                admission_number__iexact=search_term,
                status='ACTIVE'
            ).first()
        else:
            student = Student.objects.filter(
                Q(admission_number__iexact=reg_no_input) | Q(reg_no__iexact=reg_no_input),
                tenant=tenant,
                status='ACTIVE'
            ).first()
            
        if not student:
            return JsonResponse({
                'status': 'error', 
                'message': 'Student not found.'
            })
            
        # Check if allocated to transport
        if not hasattr(student, 'transport_allocation'):
             return JsonResponse({
                'status': 'error', 
                'message': f'{student.full_name} is not allocated to any transport route.'
            })

        # Mark attendance
        today = timezone.now().date()
        
        # Check if already marked for today and trip type
        existing = TransportAttendance.objects.filter(
            tenant=tenant,
            student=student,
            date=today,
            trip_type=trip_type
        ).first()
        
        if existing:
            return JsonResponse({
                'status': 'error',
                'message': f'Attendance already marked for {student.full_name} today ({trip_type})',
            })
            
        # Create attendance record
        try:
             TransportAttendance.objects.create(
                tenant=tenant,
                student=student,
                date=today,
                trip_type=trip_type,
                status='PRESENT',
                marked_by=request.user,
                remarks='QR Scan'
            )
        except Exception as e:
             return JsonResponse({'status': 'error', 'message': str(e)})
            
        return JsonResponse({
            'status': 'success',
            'message': f'Attendance marked for {student.full_name} ({trip_type})',
            'student': {
                'name': student.full_name,
                'reg_no': student.admission_number,
                'photo_url': student.user.avatar.url if student.user and student.user.avatar else None
            }
        })


class TransportFaceAttendanceView(LoginRequiredMixin, TemplateView):
    """Face recognition based transport attendance marking"""
    template_name = 'transportation/face_attendance.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        return context


@csrf_exempt
def verify_transport_face_attendance(request):
    """API to verify face against transport-allocated student database"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        import numpy as np
        import base64
        import cv2
        import os
        from apps.students.models import Student
        
        data = json.loads(request.body)
        image_data = data.get('image')
        trip_type = data.get('trip_type', 'PICKUP')
        
        if not image_data:
             return JsonResponse({'error': 'No image provided'}, status=400)
             
        # Decode base64
        if ';base64,' in image_data:
            imgstr = image_data.split(';base64,')[1] 
        else:
            imgstr = image_data
            
        nparr = np.frombuffer(base64.b64decode(imgstr), np.uint8)
        unknown_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if unknown_image is None:
             return JsonResponse({'error': 'Decoding failed'}, status=400)
        unknown_gray = cv2.cvtColor(unknown_image, cv2.COLOR_BGR2GRAY)
        
        # Init Detector
        orb = cv2.ORB_create(nfeatures=1000)
        kp1, des1 = orb.detectAndCompute(unknown_gray, None)
        
        if des1 is None:
            return JsonResponse({'match': False, 'message': 'No features detected'})
            
        # Get Students allocated to transport
        tenant = request.tenant
        students_query = Student.objects.filter(
            tenant=tenant, 
            status='ACTIVE'
        ).exclude(transport_allocation=None).select_related('user').prefetch_related('documents')
        
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        best_match_count = 0
        best_student = None
        MATCH_THRESHOLD = 15
        
        for student in students_query:
             try:
                image_path = None
                if student.user and student.user.avatar and os.path.exists(student.user.avatar.path):
                    image_path = student.user.avatar.path
                else:
                    photo_doc = student.documents.filter(doc_type='PHOTO').order_by('-created_at').first()
                    if photo_doc and photo_doc.file and os.path.exists(photo_doc.file.path):
                        image_path = photo_doc.file.path
                
                if not image_path: continue
                
                known_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                if known_image is None: continue
                
                kp2, des2 = orb.detectAndCompute(known_image, None)
                if des2 is not None:
                    matches = bf.match(des1, des2)
                    good_matches = [m for m in matches if m.distance < 50]
                    score = len(good_matches)
                    if score > best_match_count and score >= MATCH_THRESHOLD:
                        best_match_count = score
                        best_student = student
             except Exception: continue
        
        if best_student:
             today = timezone.now().date()
             # Auto-mark attendance
             TransportAttendance.objects.update_or_create(
                 student=best_student,
                 date=today,
                 trip_type=trip_type,
                 defaults={
                     'status': 'PRESENT',
                     'marked_by': request.user if request.user.is_authenticated else None,
                     'remarks': 'Marked via Face Recognition',
                     'tenant': request.tenant
                 }
             )
             
             image_url = best_student.user.avatar.url if best_student.user and best_student.user.avatar else ""
             
             return JsonResponse({
                 'match': True,
                 'name': best_student.full_name,
                 'admission_number': best_student.admission_number,
                 'image_url': image_url,
                 'message': f'Verified & Marked: {best_student.full_name}'
             })
             
        return JsonResponse({'match': False, 'message': 'No matching student found'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==================== MAINTENANCE ====================

class MaintenanceListView(BaseListView):
    model = MaintenanceRecord
    template_name = 'transportation/maintenance_list.html'
    context_object_name = 'records'
    permission_required = 'transportation.view_maintenancerecord'
    search_fields = ['vehicle__vehicle_number', 'workshop_name']
    filter_fields = ['maintenance_type', 'is_completed']

class MaintenanceCreateView(BaseCreateView):
    model = MaintenanceRecord
    form_class = MaintenanceRecordForm
    template_name = 'transportation/maintenance_form.html'
    permission_required = 'transportation.add_maintenancerecord'
    success_url = reverse_lazy('transportation:maintenance_list')

class MaintenanceUpdateView(BaseUpdateView):
    model = MaintenanceRecord
    form_class = MaintenanceRecordForm
    template_name = 'transportation/maintenance_form.html'
    permission_required = 'transportation.change_maintenancerecord'
    success_url = reverse_lazy('transportation:maintenance_list')

class MaintenanceDeleteView(BaseDeleteView):
    model = MaintenanceRecord
    template_name = 'transportation/confirm_delete.html'
    permission_required = 'transportation.delete_maintenancerecord'
    success_url = reverse_lazy('transportation:maintenance_list')


# ==================== FUEL ====================

class FuelListView(BaseListView):
    model = FuelRecord
    template_name = 'transportation/fuel_list.html'
    context_object_name = 'records'
    permission_required = 'transportation.view_fuelrecord'
    search_fields = ['vehicle__vehicle_number', 'station_name']
    filter_fields = ['fuel_type']

class FuelCreateView(BaseCreateView):
    model = FuelRecord
    form_class = FuelRecordForm
    template_name = 'transportation/fuel_form.html'
    permission_required = 'transportation.add_fuelrecord'
    success_url = reverse_lazy('transportation:fuel_list')

class FuelUpdateView(BaseUpdateView):
    model = FuelRecord
    form_class = FuelRecordForm
    template_name = 'transportation/fuel_form.html'
    permission_required = 'transportation.change_fuelrecord'
    success_url = reverse_lazy('transportation:fuel_list')

class FuelDeleteView(BaseDeleteView):
    model = FuelRecord
    template_name = 'transportation/confirm_delete.html'
    permission_required = 'transportation.delete_fuelrecord'
    success_url = reverse_lazy('transportation:fuel_list')
