from django.urls import path
from apps.events.api.views import (
    EventCategoryListCreateAPIView, EventCategoryDetailAPIView,
    EventListCreateAPIView, EventDetailAPIView,
    EventRegistrationListCreateAPIView, EventRegistrationDetailAPIView,
    EventDocumentListCreateAPIView, EventDocumentDetailAPIView,
    EventTaskListCreateAPIView, EventTaskDetailAPIView,
    EventExpenseListCreateAPIView, EventExpenseDetailAPIView,
    EventGalleryListCreateAPIView, EventGalleryDetailAPIView,
    GalleryImageListCreateAPIView, GalleryImageDetailAPIView,
    EventFeedbackListCreateAPIView, EventFeedbackDetailAPIView,
    RecurringEventPatternListCreateAPIView, RecurringEventPatternDetailAPIView
)
from .dashboard_view import EventsDashboardAPIView

urlpatterns = [
    # Dashboard
    path('dashboard/', EventsDashboardAPIView.as_view(), name='dashboard'),

    # Event Categories
    path('categories/', EventCategoryListCreateAPIView.as_view(), name='eventcategory-list'),
    path('categories/<uuid:pk>/', EventCategoryDetailAPIView.as_view(), name='eventcategory-detail'),

    # Events
    path('', EventListCreateAPIView.as_view(), name='event-list'),
    path('<uuid:slug>/', EventDetailAPIView.as_view(), name='event-detail-slug'),
    path('<uuid:pk>/', EventDetailAPIView.as_view(), name='event-detail'),

    # Registrations
    path('registrations/', EventRegistrationListCreateAPIView.as_view(), name='eventregistration-list'),
    path('registrations/<uuid:pk>/', EventRegistrationDetailAPIView.as_view(), name='eventregistration-detail'),

    # Documents
    path('documents/', EventDocumentListCreateAPIView.as_view(), name='eventdocument-list'),
    path('documents/<uuid:pk>/', EventDocumentDetailAPIView.as_view(), name='eventdocument-detail'),

    # Management
    path('tasks/', EventTaskListCreateAPIView.as_view(), name='eventtask-list'),
    path('tasks/<uuid:pk>/', EventTaskDetailAPIView.as_view(), name='eventtask-detail'),

    path('expenses/', EventExpenseListCreateAPIView.as_view(), name='eventexpense-list'),
    path('expenses/<uuid:pk>/', EventExpenseDetailAPIView.as_view(), name='eventexpense-detail'),

    # Media & Feedback
    path('galleries/', EventGalleryListCreateAPIView.as_view(), name='eventgallery-list'),
    path('galleries/<uuid:pk>/', EventGalleryDetailAPIView.as_view(), name='eventgallery-detail'),

    path('images/', GalleryImageListCreateAPIView.as_view(), name='galleryimage-list'),
    path('images/<uuid:pk>/', GalleryImageDetailAPIView.as_view(), name='galleryimage-detail'),

    path('feedback/', EventFeedbackListCreateAPIView.as_view(), name='eventfeedback-list'),
    path('feedback/<uuid:pk>/', EventFeedbackDetailAPIView.as_view(), name='eventfeedback-detail'),

    # Patterns
    path('patterns/', RecurringEventPatternListCreateAPIView.as_view(), name='recurringeventpattern-list'),
    path('patterns/<uuid:pk>/', RecurringEventPatternDetailAPIView.as_view(), name='recurringeventpattern-detail'),
]
