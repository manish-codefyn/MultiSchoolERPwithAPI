from django.urls import path
from apps.attendance import views
from apps.attendance.api.views import MarkQRAttendanceAPIView

app_name = 'attendance'

urlpatterns = [
    # Dashboard and Marking Selection
    path('dashboard/', views.AttendanceDashboardView.as_view(), name='dashboard'),
    path('mark/', views.MarkAttendanceView.as_view(), name='mark_selection'),
    path('mark/manual/', views.MarkAttendanceManualView.as_view(), name='mark_manual'),
    path('mark/qr/', views.MarkAttendanceQRView.as_view(), name='mark_qr'),
    path('mark/qr/submit/', MarkQRAttendanceAPIView.as_view(), name='mark_qr_submit'),
    path('mark/face/', views.MarkAttendanceFaceView.as_view(), name='mark_face'),
    
    # Staff QR/Face Attendance
    path('staff/mark/qr/', views.StaffMarkAttendanceQRView.as_view(), name='staff_mark_qr'),
    path('staff/mark/face/', views.StaffMarkAttendanceFaceView.as_view(), name='staff_mark_face'),
    
    # Hostel QR/Face Attendance
    path('hostel/mark/qr/', views.HostelMarkAttendanceQRView.as_view(), name='hostel_mark_qr'),
    path('hostel/mark/face/', views.HostelMarkAttendanceFaceView.as_view(), name='hostel_mark_face'),
    
    # Transport QR/Face Attendance
    path('transport/mark/qr/', views.TransportMarkAttendanceQRView.as_view(), name='transport_mark_qr'),
    path('transport/mark/face/', views.TransportMarkAttendanceFaceView.as_view(), name='transport_mark_face'),

    # Student Attendance
    path('student/', views.StudentAttendanceListView.as_view(), name='student_attendance_list'),
    path('student/<uuid:pk>/', views.StudentAttendanceDetailView.as_view(), name='student_attendance_detail'),
    path('student/create/', views.StudentAttendanceCreateView.as_view(), name='student_attendance_create'),
    path('student/<uuid:pk>/update/', views.StudentAttendanceUpdateView.as_view(), name='student_attendance_update'),
    path('student/<uuid:pk>/delete/', views.StudentAttendanceDeleteView.as_view(), name='student_attendance_delete'),

    # Staff Attendance
    path('staff/', views.StaffAttendanceListView.as_view(), name='staff_attendance_list'),
    path('staff/<uuid:pk>/', views.StaffAttendanceDetailView.as_view(), name='staff_attendance_detail'),
    path('staff/create/', views.StaffAttendanceCreateView.as_view(), name='staff_attendance_create'),
    path('staff/<uuid:pk>/update/', views.StaffAttendanceUpdateView.as_view(), name='staff_attendance_update'),
    path('staff/<uuid:pk>/delete/', views.StaffAttendanceDeleteView.as_view(), name='staff_attendance_delete'),

    # Hostel Attendance
    path('hostel/', views.HostelAttendanceListView.as_view(), name='hostel_attendance_list'),
    path('hostel/<uuid:pk>/', views.HostelAttendanceDetailView.as_view(), name='hostel_attendance_detail'),
    path('hostel/create/', views.HostelAttendanceCreateView.as_view(), name='hostel_attendance_create'),
    path('hostel/<uuid:pk>/update/', views.HostelAttendanceUpdateView.as_view(), name='hostel_attendance_update'),
    path('hostel/<uuid:pk>/delete/', views.HostelAttendanceDeleteView.as_view(), name='hostel_attendance_delete'),

    # Transport Attendance
    path('transport/', views.TransportAttendanceListView.as_view(), name='transport_attendance_list'),
    path('transport/<uuid:pk>/', views.TransportAttendanceDetailView.as_view(), name='transport_attendance_detail'),
    path('transport/create/', views.TransportAttendanceCreateView.as_view(), name='transport_attendance_create'),
    path('transport/<uuid:pk>/update/', views.TransportAttendanceUpdateView.as_view(), name='transport_attendance_update'),
    path('transport/<uuid:pk>/delete/', views.TransportAttendanceDeleteView.as_view(), name='transport_attendance_delete'),

    # Reports
    path('report/export/', views.AttendanceReportExportView.as_view(), name='report_export'),
]