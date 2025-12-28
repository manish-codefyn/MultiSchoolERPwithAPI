from django.urls import path
from apps.library.api.views import (
    LibraryListCreateAPIView, LibraryDetailAPIView,
    AuthorListCreateAPIView, AuthorDetailAPIView,
    PublisherListCreateAPIView, PublisherDetailAPIView,
    BookCategoryListCreateAPIView, BookCategoryDetailAPIView,
    BookListCreateAPIView, BookDetailAPIView,
    BookCopyListCreateAPIView, BookCopyDetailAPIView,
    BookIssueListCreateAPIView, BookIssueDetailAPIView,
    ReservationListCreateAPIView, ReservationDetailAPIView,
    FineListCreateAPIView, FineDetailAPIView,
    FinePaymentListCreateAPIView, FinePaymentDetailAPIView,
    LibraryMemberListCreateAPIView, LibraryMemberDetailAPIView,
    LibraryReportListCreateAPIView, LibraryReportDetailAPIView
)


urlpatterns = [
    # Libraries
    path('', LibraryListCreateAPIView.as_view(), name='library-list'),
    path('<uuid:pk>/', LibraryDetailAPIView.as_view(), name='library-detail'),

    # Catalog Management
    path('authors/', AuthorListCreateAPIView.as_view(), name='author-list'),
    path('authors/<uuid:pk>/', AuthorDetailAPIView.as_view(), name='author-detail'),
    
    path('publishers/', PublisherListCreateAPIView.as_view(), name='publisher-list'),
    path('publishers/<uuid:pk>/', PublisherDetailAPIView.as_view(), name='publisher-detail'),
    
    path('categories/', BookCategoryListCreateAPIView.as_view(), name='category-list'),
    path('categories/<uuid:pk>/', BookCategoryDetailAPIView.as_view(), name='category-detail'),

    # Books & Copies
    path('books/', BookListCreateAPIView.as_view(), name='book-list'),
    path('books/<uuid:pk>/', BookDetailAPIView.as_view(), name='book-detail'),
    
    path('copies/', BookCopyListCreateAPIView.as_view(), name='bookcopy-list'),
    path('copies/<uuid:pk>/', BookCopyDetailAPIView.as_view(), name='bookcopy-detail'),

    # Circulation
    path('issues/', BookIssueListCreateAPIView.as_view(), name='bookissue-list'),
    path('issues/<uuid:pk>/', BookIssueDetailAPIView.as_view(), name='bookissue-detail'),
    
    path('reservations/', ReservationListCreateAPIView.as_view(), name='reservation-list'),
    path('reservations/<uuid:pk>/', ReservationDetailAPIView.as_view(), name='reservation-detail'),

    # Fines & Members
    path('fines/', FineListCreateAPIView.as_view(), name='fine-list'),
    path('fines/<uuid:pk>/', FineDetailAPIView.as_view(), name='fine-detail'),
    
    path('payments/', FinePaymentListCreateAPIView.as_view(), name='finepayment-list'),
    path('payments/<uuid:pk>/', FinePaymentDetailAPIView.as_view(), name='finepayment-detail'),
    
    path('members/', LibraryMemberListCreateAPIView.as_view(), name='librarymember-list'),
    path('members/<uuid:pk>/', LibraryMemberDetailAPIView.as_view(), name='librarymember-detail'),

    # Reports
    path('reports/', LibraryReportListCreateAPIView.as_view(), name='libraryreport-list'),
    path('reports/<uuid:pk>/', LibraryReportDetailAPIView.as_view(), name='libraryreport-detail'),
]
