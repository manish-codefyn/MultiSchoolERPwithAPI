from django.urls import path
from . import views

urlpatterns = [
    # Student Attendance
    path('student/', views.StudentAttendanceListCreateAPIView.as_view(), name='student-attendance-list'),
    path('student/<uuid:pk>/', views.StudentAttendanceDetailAPIView.as_view(), name='student-attendance-detail'),
    
    # Staff Attendance
    path('staff/', views.StaffAttendanceListCreateAPIView.as_view(), name='staff-attendance-list'),
    path('staff/<uuid:pk>/', views.StaffAttendanceDetailAPIView.as_view(), name='staff-attendance-detail'),
    
    # Hostel Attendance
    path('hostel/', views.HostelAttendanceListCreateAPIView.as_view(), name='hostel-attendance-list'),
    path('hostel/<uuid:pk>/', views.HostelAttendanceDetailAPIView.as_view(), name='hostel-attendance-detail'),
    
    # Transport Attendance
    path('transport/', views.TransportAttendanceListCreateAPIView.as_view(), name='transport-attendance-list'),
    path('transport/<uuid:pk>/', views.TransportAttendanceDetailAPIView.as_view(), name='transport-attendance-detail'),
    
    # QR Attendance
    path('mark/qr/', views.MarkQRAttendanceAPIView.as_view(), name='mark-qr-attendance'),
    
    # Face Recognition (DeepFace)
    path('mark-face/', views.MarkFaceAttendanceAPIView.as_view(), name='mark-face-attendance-alias'), # Support for Flutter App
    path('mark/face/', views.MarkFaceAttendanceAPIView.as_view(), name='mark-face-attendance'),  # Legacy
    path('mark/deepface/', views.MarkDeepFaceAttendanceAPIView.as_view(), name='mark-deepface-attendance'),  # New DeepFace
    path('mark/deepface/batch/', views.DeepFaceBatchRecognitionAPIView.as_view(), name='deepface-batch-recognition'),
    
    # Bulk/Manual Attendance
    path('students/by-class/', views.StudentListByClassAPIView.as_view(), name='student-list-by-class'),
    path('bulk/update/', views.BulkAttendanceUpdateAPIView.as_view(), name='bulk-attendance-update'),
    
    # Dashboard & Reporting
    path('stats/', views.AttendanceStatsAPIView.as_view(), name='attendance-stats'),
    path('history/', views.AttendanceHistoryListAPIView.as_view(), name='attendance-history'),
    path('export/', views.AttendanceExportAPIView.as_view(), name='attendance-export'),
    path('dashboard/', views.AttendanceDashboardAPIView.as_view(), name='attendance-dashboard'),
]