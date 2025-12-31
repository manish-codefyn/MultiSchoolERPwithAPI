from django.urls import path
from .views import (
    StudentDashboardView,
    PortalInvoiceListView,
    PortalPaymentInitiateView,
    PortalPaymentCallbackView,
    PortalTimetableView,
    PortalAssignmentListView,
    PortalAssignmentDetailView,
    PortalAssignmentSubmitView,
    PortalGamesView,
    MemoryGameView,
    MathQuizView,
    TicTacToeView,
    StudentProfileView,
    PortalInboxView,
    PortalThreadDetailView,
    PortalInvoicePrintView,
    PortalInvoiceDownloadView,
    PortalDirectPaymentInitiateView,
    PortalSyllabusListView
)

app_name = 'student_portal'

urlpatterns = [
    path('dashboard/', StudentDashboardView.as_view(), name='dashboard'),
    path('profile/', StudentProfileView.as_view(), name='profile'),
    
    # Financials
    path('finance/invoices/', PortalInvoiceListView.as_view(), name='invoice_list'),
    path('finance/payment/direct/', PortalDirectPaymentInitiateView.as_view(), name='direct_payment'),
    path('finance/invoices/<uuid:pk>/pay/', PortalPaymentInitiateView.as_view(), name='pay_invoice'),
    path('finance/invoices/<uuid:pk>/print/', PortalInvoicePrintView.as_view(), name='print_invoice'),
    path('finance/invoices/<uuid:pk>/download/', PortalInvoiceDownloadView.as_view(), name='download_invoice'),
    path('finance/payment/callback/', PortalPaymentCallbackView.as_view(), name='payment_callback'),
    
    # Academics
    path('academics/timetable/', PortalTimetableView.as_view(), name='timetable'),
    path('academics/assignments/', PortalAssignmentListView.as_view(), name='assignments'),
    path('academics/assignments/<uuid:pk>/', PortalAssignmentDetailView.as_view(), name='assignment_detail'),
    path('academics/assignments/<uuid:pk>/submit/', PortalAssignmentSubmitView.as_view(), name='assignment_submit'),
    path('academics/syllabus/', PortalSyllabusListView.as_view(), name='syllabus_list'),
    
    # Games
    path('games/', PortalGamesView.as_view(), name='games'),
    path('games/memory/', MemoryGameView.as_view(), name='games_memory'),
    path('games/quiz/', MathQuizView.as_view(), name='games_quiz'),
    path('games/quiz/', MathQuizView.as_view(), name='games_quiz'),
    path('games/tictactoe/', TicTacToeView.as_view(), name='games_tictactoe'),

    # Communications
    path('communications/inbox/', PortalInboxView.as_view(), name='inbox'),
    path('communications/thread/<uuid:pk>/', PortalThreadDetailView.as_view(), name='thread_detail'),
]
