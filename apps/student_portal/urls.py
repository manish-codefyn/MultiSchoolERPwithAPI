from django.urls import path
from .views import (
    StudentDashboardView,
    PortalInvoiceListView,
    PortalPaymentInitiateView,
    PortalPaymentCallbackView,
    PortalTimetableView,
    PortalTimetableView,
    PortalGamesView,
    MemoryGameView,
    MathQuizView,
    TicTacToeView,
    StudentProfileView
)

app_name = 'student_portal'

urlpatterns = [
    path('dashboard/', StudentDashboardView.as_view(), name='dashboard'),
    path('profile/', StudentProfileView.as_view(), name='profile'),
    
    # Financials
    path('finance/invoices/', PortalInvoiceListView.as_view(), name='invoice_list'),
    path('finance/pay/<int:pk>/', PortalPaymentInitiateView.as_view(), name='pay_invoice'),
    path('finance/callback/', PortalPaymentCallbackView.as_view(), name='payment_callback'),
    
    # Academics
    path('academics/timetable/', PortalTimetableView.as_view(), name='timetable'),
    
    # Games
    path('games/', PortalGamesView.as_view(), name='games'),
    path('games/memory/', MemoryGameView.as_view(), name='games_memory'),
    path('games/quiz/', MathQuizView.as_view(), name='games_quiz'),
    path('games/tictactoe/', TicTacToeView.as_view(), name='games_tictactoe'),
]
