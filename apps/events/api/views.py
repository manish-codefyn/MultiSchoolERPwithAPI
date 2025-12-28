from rest_framework import status
from rest_framework.response import Response
from apps.core.api.views import (
    BaseListCreateAPIView, BaseRetrieveUpdateDestroyAPIView
)
from apps.events.models import (
    EventCategory, Event, EventRegistration, EventDocument,
    EventTask, EventExpense, EventGallery, GalleryImage,
    EventFeedback, RecurringEventPattern
)
from apps.events.api.serializers import (
    EventCategorySerializer, EventSerializer, EventRegistrationSerializer,
    EventDocumentSerializer, EventTaskSerializer, EventExpenseSerializer,
    EventGallerySerializer, GalleryImageSerializer, EventFeedbackSerializer,
    RecurringEventPatternSerializer
)

# ============================================================================
# EVENT CONFIG VIEWS
# ============================================================================

class EventCategoryListCreateAPIView(BaseListCreateAPIView):
    model = EventCategory
    serializer_class = EventCategorySerializer
    search_fields = ['name', 'code']
    roles_required = ['admin', 'event_manager', 'teacher']

class EventCategoryDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = EventCategory
    serializer_class = EventCategorySerializer
    roles_required = ['admin', 'event_manager']

# ============================================================================
# EVENT CORE VIEWS
# ============================================================================

class EventListCreateAPIView(BaseListCreateAPIView):
    model = Event
    serializer_class = EventSerializer
    search_fields = ['title', 'description', 'venue']
    filterset_fields = ['event_type', 'category', 'status', 'is_published', 'is_active']
    roles_required = ['admin', 'event_manager', 'teacher', 'student', 'parent']

class EventDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Event
    serializer_class = EventSerializer
    roles_required = ['admin', 'event_manager']


class EventRegistrationListCreateAPIView(BaseListCreateAPIView):
    model = EventRegistration
    serializer_class = EventRegistrationSerializer
    search_fields = ['student__first_name', 'external_name']
    filterset_fields = ['event', 'registration_type', 'status', 'is_active']
    roles_required = ['admin', 'event_manager', 'teacher', 'student', 'parent']

class EventRegistrationDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = EventRegistration
    serializer_class = EventRegistrationSerializer
    roles_required = ['admin', 'event_manager']


class EventDocumentListCreateAPIView(BaseListCreateAPIView):
    model = EventDocument
    serializer_class = EventDocumentSerializer
    search_fields = ['name']
    filterset_fields = ['event', 'document_type', 'is_public']
    roles_required = ['admin', 'event_manager', 'teacher', 'student']

class EventDocumentDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = EventDocument
    serializer_class = EventDocumentSerializer
    roles_required = ['admin', 'event_manager']

# ============================================================================
# EVENT MANAGEMENT VIEWS
# ============================================================================

class EventTaskListCreateAPIView(BaseListCreateAPIView):
    model = EventTask
    serializer_class = EventTaskSerializer
    search_fields = ['title']
    filterset_fields = ['event', 'assigned_to', 'priority', 'status']
    roles_required = ['admin', 'event_manager', 'teacher']

class EventTaskDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = EventTask
    serializer_class = EventTaskSerializer
    roles_required = ['admin', 'event_manager']


class EventExpenseListCreateAPIView(BaseListCreateAPIView):
    model = EventExpense
    serializer_class = EventExpenseSerializer
    search_fields = ['description', 'vendor_name']
    filterset_fields = ['event', 'category', 'payment_status']
    roles_required = ['admin', 'event_manager']

class EventExpenseDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = EventExpense
    serializer_class = EventExpenseSerializer
    roles_required = ['admin', 'event_manager']

# ============================================================================
# EVENT MEDIA & FEEDBACK VIEWS
# ============================================================================

class EventGalleryListCreateAPIView(BaseListCreateAPIView):
    model = EventGallery
    serializer_class = EventGallerySerializer
    search_fields = ['title']
    filterset_fields = ['event', 'is_published', 'is_featured']
    roles_required = ['admin', 'event_manager', 'teacher', 'student', 'parent']

class EventGalleryDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = EventGallery
    serializer_class = EventGallerySerializer
    roles_required = ['admin', 'event_manager']


class GalleryImageListCreateAPIView(BaseListCreateAPIView):
    model = GalleryImage
    serializer_class = GalleryImageSerializer
    filterset_fields = ['gallery', 'is_featured']
    roles_required = ['admin', 'event_manager', 'teacher', 'student', 'parent']

class GalleryImageDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = GalleryImage
    serializer_class = GalleryImageSerializer
    roles_required = ['admin', 'event_manager']


class EventFeedbackListCreateAPIView(BaseListCreateAPIView):
    model = EventFeedback
    serializer_class = EventFeedbackSerializer
    filterset_fields = ['event', 'overall_rating', 'is_approved']
    roles_required = ['admin', 'event_manager', 'teacher', 'student', 'parent']

class EventFeedbackDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = EventFeedback
    serializer_class = EventFeedbackSerializer
    roles_required = ['admin', 'event_manager']


class RecurringEventPatternListCreateAPIView(BaseListCreateAPIView):
    model = RecurringEventPattern
    serializer_class = RecurringEventPatternSerializer
    filterset_fields = ['base_event', 'recurrence_type', 'is_active']
    roles_required = ['admin', 'event_manager']

class RecurringEventPatternDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = RecurringEventPattern
    serializer_class = RecurringEventPatternSerializer
    roles_required = ['admin', 'event_manager']
