from django.urls import path
from apps.hostel.api.views import (
    AmenityListCreateAPIView, AmenityDetailAPIView,
    FacilityListCreateAPIView, FacilityDetailAPIView,
    HostelListCreateAPIView, HostelDetailAPIView,
    RoomListCreateAPIView, RoomDetailAPIView,
    HostelAllocationListCreateAPIView, HostelAllocationDetailAPIView,
    HostelAttendanceListCreateAPIView, HostelAttendanceDetailAPIView,
    LeaveApplicationListCreateAPIView, LeaveApplicationDetailAPIView,
    MessMenuCategoryListCreateAPIView, MessMenuCategoryDetailAPIView,
    MessMenuItemListCreateAPIView, MessMenuItemDetailAPIView,
    DailyMessMenuListCreateAPIView, DailyMessMenuDetailAPIView,
    DailyMenuItemListCreateAPIView, DailyMenuItemDetailAPIView,
    HostelMessSubscriptionListCreateAPIView, HostelMessSubscriptionDetailAPIView,
    MessAttendanceListCreateAPIView, MessAttendanceDetailAPIView,
    MessAttendanceListCreateAPIView, MessAttendanceDetailAPIView,
    MessFeedbackListCreateAPIView, MessFeedbackDetailAPIView
)
from .dashboard_view import HostelDashboardAPIView


urlpatterns = [
    # Dashboard
    path('dashboard/', HostelDashboardAPIView.as_view(), name='dashboard'),

    # Infrastructure
    path('amenities/', AmenityListCreateAPIView.as_view(), name='amenity-list'),
    path('amenities/<uuid:pk>/', AmenityDetailAPIView.as_view(), name='amenity-detail'),
    
    path('facilities/', FacilityListCreateAPIView.as_view(), name='facility-list'),
    path('facilities/<uuid:pk>/', FacilityDetailAPIView.as_view(), name='facility-detail'),
    
    path('hostels/', HostelListCreateAPIView.as_view(), name='hostel-list'),
    path('hostels/<uuid:pk>/', HostelDetailAPIView.as_view(), name='hostel-detail'),
    
    path('rooms/', RoomListCreateAPIView.as_view(), name='room-list'),
    path('rooms/<uuid:pk>/', RoomDetailAPIView.as_view(), name='room-detail'),

    # Allocations & Attendance
    path('allocations/', HostelAllocationListCreateAPIView.as_view(), name='hostelallocation-list'),
    path('allocations/<uuid:pk>/', HostelAllocationDetailAPIView.as_view(), name='hostelallocation-detail'),
    
    path('attendance/', HostelAttendanceListCreateAPIView.as_view(), name='hostelattendance-list'),
    path('attendance/<uuid:pk>/', HostelAttendanceDetailAPIView.as_view(), name='hostelattendance-detail'),
    
    path('leaves/', LeaveApplicationListCreateAPIView.as_view(), name='leaveapplication-list'),
    path('leaves/<uuid:pk>/', LeaveApplicationDetailAPIView.as_view(), name='leaveapplication-detail'),

    # Mess Management
    path('mess/categories/', MessMenuCategoryListCreateAPIView.as_view(), name='messmenucategory-list'),
    path('mess/categories/<uuid:pk>/', MessMenuCategoryDetailAPIView.as_view(), name='messmenucategory-detail'),
    
    path('mess/items/', MessMenuItemListCreateAPIView.as_view(), name='messmenuitem-list'),
    path('mess/items/<uuid:pk>/', MessMenuItemDetailAPIView.as_view(), name='messmenuitem-detail'),
    
    path('mess/daily/', DailyMessMenuListCreateAPIView.as_view(), name='dailymessmenu-list'),
    path('mess/daily/<uuid:pk>/', DailyMessMenuDetailAPIView.as_view(), name='dailymessmenu-detail'),

    path('mess/daily-items/', DailyMenuItemListCreateAPIView.as_view(), name='dailymenuitem-list'),
    path('mess/daily-items/<uuid:pk>/', DailyMenuItemDetailAPIView.as_view(), name='dailymenuitem-detail'),

    # Mess Subscriptions & Attendance
    path('mess/subscriptions/', HostelMessSubscriptionListCreateAPIView.as_view(), name='hostelmesssubscription-list'),
    path('mess/subscriptions/<uuid:pk>/', HostelMessSubscriptionDetailAPIView.as_view(), name='hostelmesssubscription-detail'),
    
    path('mess/attendance/', MessAttendanceListCreateAPIView.as_view(), name='messattendance-list'),
    path('mess/attendance/<uuid:pk>/', MessAttendanceDetailAPIView.as_view(), name='messattendance-detail'),
    
    path('mess/feedback/', MessFeedbackListCreateAPIView.as_view(), name='messfeedback-list'),
    path('mess/feedback/<uuid:pk>/', MessFeedbackDetailAPIView.as_view(), name='messfeedback-detail'),
]
