from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.api.serializers import TenantAwareSerializer, RelatedFieldAlternative
from apps.library.models import (
    Library, Author, Publisher, BookCategory, Book, BookCopy,
    BookIssue, Reservation, Fine, FinePayment, LibraryMember,
    LibraryReport
)

User = get_user_model()

# ============================================================================
# HELPER SERIALIZERS
# ============================================================================

class SimpleUserSerializer(serializers.ModelSerializer):
    """Simple serializer for user details"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role']

# ============================================================================
# CATALOG SERIALIZERS
# ============================================================================

class LibrarySerializer(TenantAwareSerializer):
    librarian_detail = RelatedFieldAlternative(
        source='librarian',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    
    # Computed
    total_books = serializers.IntegerField(read_only=True)
    available_books = serializers.IntegerField(read_only=True)
    issued_books = serializers.IntegerField(read_only=True)

    class Meta:
        model = Library
        fields = '__all__'
        read_only_fields = ['id', 'total_books', 'available_books', 'issued_books']

class AuthorSerializer(TenantAwareSerializer):
    books_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Author
        fields = '__all__'
        read_only_fields = ['id', 'books_count']

class PublisherSerializer(TenantAwareSerializer):
    books_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Publisher
        fields = '__all__'
        read_only_fields = ['id', 'books_count']

class BookCategorySerializer(TenantAwareSerializer):
    parent_category_detail = RelatedFieldAlternative(
        source='parent_category',
        read_only=True,
        serializer='self'
    )
    books_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = BookCategory
        fields = '__all__'
        read_only_fields = ['id', 'books_count']

class BookSerializer(TenantAwareSerializer):
    category_detail = RelatedFieldAlternative(
        source='category',
        read_only=True,
        serializer=BookCategorySerializer
    )
    publisher_detail = RelatedFieldAlternative(
        source='publisher',
        read_only=True,
        serializer=PublisherSerializer
    )
    # M2M Relationships
    authors_detail = AuthorSerializer(source='authors', many=True, read_only=True)
    
    # Validation helpers via computed props
    can_be_issued = serializers.BooleanField(read_only=True)
    authors_display = serializers.CharField(read_only=True)

    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ['id', 'can_be_issued', 'authors_display', 'available_copies']

class BookCopySerializer(TenantAwareSerializer):
    book_detail = RelatedFieldAlternative(
        source='book',
        read_only=True,
        serializer=BookSerializer
    )
    
    can_be_issued = serializers.BooleanField(read_only=True)

    class Meta:
        model = BookCopy
        fields = '__all__'
        read_only_fields = ['id', 'can_be_issued']

# ============================================================================
# CIRCULATION SERIALIZERS
# ============================================================================

class BookIssueSerializer(TenantAwareSerializer):
    member_detail = RelatedFieldAlternative(
        source='member',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    book_copy_detail = RelatedFieldAlternative(
        source='book_copy',
        read_only=True,
        serializer=BookCopySerializer
    )
    issued_by_detail = RelatedFieldAlternative(
        source='issued_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    received_by_detail = RelatedFieldAlternative(
        source='received_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    
    # Computed
    is_overdue = serializers.BooleanField(read_only=True)
    overdue_days = serializers.IntegerField(read_only=True)
    calculated_fine = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    pending_fine = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = BookIssue
        fields = '__all__'
        read_only_fields = ['id', 'issue_number', 'is_overdue', 'overdue_days', 'calculated_fine', 'pending_fine']

class ReservationSerializer(TenantAwareSerializer):
    book_detail = RelatedFieldAlternative(
        source='book',
        read_only=True,
        serializer=BookSerializer
    )
    member_detail = RelatedFieldAlternative(
        source='member',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = Reservation
        fields = '__all__'

# ============================================================================
# MEMBER & FINES
# ============================================================================

class LibraryMemberSerializer(TenantAwareSerializer):
    user_detail = RelatedFieldAlternative(
        source='user',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = LibraryMember
        fields = '__all__'

class FineSerializer(TenantAwareSerializer):
    member_detail = RelatedFieldAlternative(
        source='member',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    book_issue_detail = RelatedFieldAlternative(
        source='book_issue',
        read_only=True,
        serializer=BookIssueSerializer
    )

    class Meta:
        model = Fine
        fields = '__all__'

class FinePaymentSerializer(TenantAwareSerializer):
    fine_detail = RelatedFieldAlternative(
        source='fine',
        read_only=True,
        serializer=FineSerializer
    )
    collected_by_detail = RelatedFieldAlternative(
        source='collected_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = FinePayment
        fields = '__all__'

class LibraryReportSerializer(TenantAwareSerializer):
    generated_by_detail = RelatedFieldAlternative(
        source='generated_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = LibraryReport
        fields = '__all__'
