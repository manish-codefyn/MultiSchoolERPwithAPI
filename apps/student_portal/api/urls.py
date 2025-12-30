from django.urls import path
from .views import (
    StudentDashboardAPIView,
    StudentProfileAPIView,
    InvoiceListAPIView,
    InvoiceDetailAPIView,
    AssignmentListAPIView,
    AssignmentDetailAPIView,
    AssignmentSubmitAPIView,
    TimetableAPIView,
    InboxAPIView,
    ThreadDetailAPIView,
    SendMessageAPIView,
    NotificationListAPIView,
    MarkNotificationReadAPIView,
    AttendanceListAPIView,
    HostelDetailsAPIView,
    HostelListAPIView,
    ExamListAPIView,
    ExamResultListAPIView,
    ExamResultDetailAPIView,
)

app_name = 'student_portal_api'

urlpatterns = [
    # Dashboard
    path('dashboard/', StudentDashboardAPIView.as_view(), name='dashboard'),
    
    # Profile
    path('profile/', StudentProfileAPIView.as_view(), name='profile'),
    
    # Invoices
    path('invoices/', InvoiceListAPIView.as_view(), name='invoice_list'),
    path('invoices/<uuid:pk>/', InvoiceDetailAPIView.as_view(), name='invoice_detail'),
    
    # Assignments
    path('assignments/', AssignmentListAPIView.as_view(), name='assignment_list'),
    path('assignments/<uuid:pk>/', AssignmentDetailAPIView.as_view(), name='assignment_detail'),
    path('assignments/<uuid:pk>/submit/', AssignmentSubmitAPIView.as_view(), name='assignment_submit'),
    
    # Timetable
    path('timetable/', TimetableAPIView.as_view(), name='timetable'),
    
    # Communications
    path('inbox/', InboxAPIView.as_view(), name='inbox'),
    path('threads/<uuid:pk>/', ThreadDetailAPIView.as_view(), name='thread_detail'),
    path('threads/<uuid:pk>/send/', SendMessageAPIView.as_view(), name='send_message'),
    
    # Notifications
    path('notifications/', NotificationListAPIView.as_view(), name='notifications'),
    path('notifications/<uuid:pk>/read/', MarkNotificationReadAPIView.as_view(), name='mark_notification_read'),
    
    # Attendance
    path('attendance/', AttendanceListAPIView.as_view(), name='attendance_list'),
    
    # Hostel
    path('hostel/details/', HostelDetailsAPIView.as_view(), name='hostel_details'),
    path('hostel/list/', HostelListAPIView.as_view(), name='hostel_list'),
    
    # Exams & Results
    path('exams/', ExamListAPIView.as_view(), name='exam_list'),
    path('results/', ExamResultListAPIView.as_view(), name='result_list'),
    path('results/<uuid:pk>/', ExamResultDetailAPIView.as_view(), name='result_detail'),
]
