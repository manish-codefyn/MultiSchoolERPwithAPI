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
]
