from rest_framework import status
from rest_framework.response import Response
from apps.core.api.views import (
    BaseListCreateAPIView, BaseRetrieveUpdateDestroyAPIView
)
from apps.library.models import (
    Library, Author, Publisher, BookCategory, Book, BookCopy,
    BookIssue, Reservation, Fine, FinePayment, LibraryMember,
    LibraryReport
)
from apps.library.api.serializers import (
    LibrarySerializer, AuthorSerializer, PublisherSerializer,
    BookCategorySerializer, BookSerializer, BookCopySerializer,
    BookIssueSerializer, ReservationSerializer, FineSerializer,
    FinePaymentSerializer, LibraryMemberSerializer, LibraryReportSerializer
)

# ============================================================================
# CATALOG VIEWS
# ============================================================================

class LibraryListCreateAPIView(BaseListCreateAPIView):
    model = Library
    serializer_class = LibrarySerializer
    roles_required = ['admin', 'librarian']

class LibraryDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Library
    serializer_class = LibrarySerializer
    roles_required = ['admin', 'librarian']


class AuthorListCreateAPIView(BaseListCreateAPIView):
    model = Author
    serializer_class = AuthorSerializer
    search_fields = ['name']
    roles_required = ['admin', 'librarian', 'teacher', 'student']

class AuthorDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Author
    serializer_class = AuthorSerializer
    roles_required = ['admin', 'librarian']


class PublisherListCreateAPIView(BaseListCreateAPIView):
    model = Publisher
    serializer_class = PublisherSerializer
    search_fields = ['name']
    roles_required = ['admin', 'librarian', 'teacher', 'student']

class PublisherDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Publisher
    serializer_class = PublisherSerializer
    roles_required = ['admin', 'librarian']


class BookCategoryListCreateAPIView(BaseListCreateAPIView):
    model = BookCategory
    serializer_class = BookCategorySerializer
    search_fields = ['name']
    roles_required = ['admin', 'librarian', 'teacher', 'student']

class BookCategoryDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = BookCategory
    serializer_class = BookCategorySerializer
    roles_required = ['admin', 'librarian']


class BookListCreateAPIView(BaseListCreateAPIView):
    model = Book
    serializer_class = BookSerializer
    search_fields = ['title', 'isbn', 'authors__name']
    filterset_fields = ['category', 'publisher', 'language', 'book_type']
    roles_required = ['admin', 'librarian', 'teacher', 'student']

class BookDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Book
    serializer_class = BookSerializer
    roles_required = ['admin', 'librarian']


class BookCopyListCreateAPIView(BaseListCreateAPIView):
    model = BookCopy
    serializer_class = BookCopySerializer
    search_fields = ['accession_number', 'barcode', 'book__title']
    filterset_fields = ['book', 'status', 'condition']
    roles_required = ['admin', 'librarian', 'teacher', 'student']

class BookCopyDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = BookCopy
    serializer_class = BookCopySerializer
    roles_required = ['admin', 'librarian']

# ============================================================================
# CIRCULATION VIEWS
# ============================================================================

class BookIssueListCreateAPIView(BaseListCreateAPIView):
    model = BookIssue
    serializer_class = BookIssueSerializer
    search_fields = ['issue_number', 'member__first_name', 'book_copy__accession_number']
    filterset_fields = ['status', 'member', 'issue_date', 'due_date']
    roles_required = ['admin', 'librarian', 'teacher', 'student']

class BookIssueDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = BookIssue
    serializer_class = BookIssueSerializer
    roles_required = ['admin', 'librarian']


class ReservationListCreateAPIView(BaseListCreateAPIView):
    model = Reservation
    serializer_class = ReservationSerializer
    roles_required = ['admin', 'librarian', 'teacher', 'student']

class ReservationDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Reservation
    serializer_class = ReservationSerializer
    roles_required = ['admin', 'librarian']

# ============================================================================
# FINE & REPORT VIEWS
# ============================================================================

class FineListCreateAPIView(BaseListCreateAPIView):
    model = Fine
    serializer_class = FineSerializer
    roles_required = ['admin', 'librarian']

class FineDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Fine
    serializer_class = FineSerializer
    roles_required = ['admin', 'librarian']


class FinePaymentListCreateAPIView(BaseListCreateAPIView):
    model = FinePayment
    serializer_class = FinePaymentSerializer
    roles_required = ['admin', 'librarian']

class FinePaymentDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = FinePayment
    serializer_class = FinePaymentSerializer
    roles_required = ['admin', 'librarian']


class LibraryMemberListCreateAPIView(BaseListCreateAPIView):
    model = LibraryMember
    serializer_class = LibraryMemberSerializer
    roles_required = ['admin', 'librarian']

class LibraryMemberDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = LibraryMember
    serializer_class = LibraryMemberSerializer
    roles_required = ['admin', 'librarian']


class LibraryReportListCreateAPIView(BaseListCreateAPIView):
    model = LibraryReport
    serializer_class = LibraryReportSerializer
    roles_required = ['admin', 'librarian']

class LibraryReportDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = LibraryReport
    serializer_class = LibraryReportSerializer
    roles_required = ['admin', 'librarian']
