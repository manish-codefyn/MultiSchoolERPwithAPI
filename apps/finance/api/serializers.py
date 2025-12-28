from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.api.serializers import TenantAwareSerializer, RelatedFieldAlternative
from apps.finance.models import (
    FeeStructure, FeeDiscount, Invoice, InvoiceItem, AppliedDiscount,
    Payment, Refund, ExpenseCategory, Expense, Budget, BudgetCategory,
    BudgetItem, BudgetTemplate, BudgetTemplateItem, FinancialTransaction,
    BankAccount, FinancialReport
)
from apps.academics.api.serializers import (
    AcademicYearSerializer, SchoolClassSerializer
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
# FEE STRUCTURE & DISCOUNTS
# ============================================================================

class FeeStructureSerializer(TenantAwareSerializer):
    academic_year_detail = RelatedFieldAlternative(
        source='academic_year',
        read_only=True,
        serializer=AcademicYearSerializer
    )
    class_name_detail = RelatedFieldAlternative(
        source='class_name',
        read_only=True,
        serializer=SchoolClassSerializer
    )
    # Calculated Fields
    total_fee_per_year = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = FeeStructure
        fields = '__all__'
        ref_name = "FinanceAPIFeeStructureSerializer"

class FeeDiscountSerializer(TenantAwareSerializer):
    class Meta:
        model = FeeDiscount
        fields = '__all__'
        ref_name = "FinanceAPIFeeDiscountSerializer"

# ============================================================================
# INVOICE & PAYMENTS
# ============================================================================

class InvoiceItemSerializer(TenantAwareSerializer):
    fee_structure_detail = RelatedFieldAlternative(
        source='fee_structure',
        read_only=True,
        serializer=FeeStructureSerializer
    )

    class Meta:
        model = InvoiceItem
        fields = '__all__'
        ref_name = "FinanceAPIInvoiceItemSerializer"

class AppliedDiscountSerializer(TenantAwareSerializer):
    discount_detail = RelatedFieldAlternative(
        source='discount',
        read_only=True,
        serializer=FeeDiscountSerializer
    )

    class Meta:
        model = AppliedDiscount
        fields = '__all__'
        ref_name = "FinanceAPIAppliedDiscountSerializer"

class InvoiceSerializer(TenantAwareSerializer):
    academic_year_detail = RelatedFieldAlternative(
        source='academic_year',
        read_only=True,
        serializer=AcademicYearSerializer
    )
    class_name_detail = RelatedFieldAlternative(
        source='class_name',
        read_only=True,
        serializer=SchoolClassSerializer
    )
    # Nested Items
    items = InvoiceItemSerializer(many=True, read_only=True)
    applied_discounts = AppliedDiscountSerializer(many=True, read_only=True)
    
    # Simple Student info (avoiding full serializer import to prevent circular deps if any)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_admission_number = serializers.CharField(source='student.admission_number', read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'
        ref_name = "FinanceAPIInvoiceSerializer"

class PaymentSerializer(TenantAwareSerializer):
    invoice_detail = RelatedFieldAlternative(
        source='invoice',
        read_only=True,
        serializer=InvoiceSerializer
    )
    received_by_detail = RelatedFieldAlternative(
        source='received_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = Payment
        fields = '__all__'
        ref_name = "FinanceAPIPaymentSerializer"

class RefundSerializer(TenantAwareSerializer):
    payment_detail = RelatedFieldAlternative(
        source='payment',
        read_only=True,
        serializer=PaymentSerializer
    )
    approved_by_detail = RelatedFieldAlternative(
        source='approved_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    processed_by_detail = RelatedFieldAlternative(
        source='processed_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = Refund
        fields = '__all__'
        ref_name = "FinanceAPIRefundSerializer"

# ============================================================================
# EXPENSES & BUDGET
# ============================================================================

class ExpenseCategorySerializer(TenantAwareSerializer):
    class Meta:
        model = ExpenseCategory
        fields = '__all__'
        ref_name = "FinanceAPIExpenseCategorySerializer"

class ExpenseSerializer(TenantAwareSerializer):
    category_detail = RelatedFieldAlternative(
        source='category',
        read_only=True,
        serializer=ExpenseCategorySerializer
    )
    recorded_by_detail = RelatedFieldAlternative(
        source='recorded_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    approved_by_detail = RelatedFieldAlternative(
        source='approved_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = Expense
        fields = '__all__'
        ref_name = "FinanceAPIExpense"

class BudgetSerializer(TenantAwareSerializer):
    academic_year_detail = RelatedFieldAlternative(
        source='academic_year',
        read_only=True,
        serializer=AcademicYearSerializer
    )

    class Meta:
        model = Budget
        fields = '__all__'
        ref_name = "FinanceAPIBudgetSerializer"

class BudgetCategorySerializer(TenantAwareSerializer):
    parent_category_detail = RelatedFieldAlternative(
        source='parent_category',
        read_only=True,
        serializer='self' # Recursive
    )

    class Meta:
        model = BudgetCategory
        fields = '__all__'
        ref_name = "FinanceAPIBudgetCategorySerializer"

class BudgetItemSerializer(TenantAwareSerializer):
    budget_detail = RelatedFieldAlternative(
        source='budget',
        read_only=True,
        serializer=BudgetSerializer
    )
    category_detail = RelatedFieldAlternative(
        source='category',
        read_only=True,
        serializer=BudgetCategorySerializer
    )

    class Meta:
        model = BudgetItem
        fields = '__all__'
        ref_name = "FinanceAPIBudgetItemSerializer"

class BudgetTemplateSerializer(TenantAwareSerializer):
    class Meta:
        model = BudgetTemplate
        fields = '__all__'
        ref_name = "FinanceAPIBudgetTemplateSerializer"

class BudgetTemplateItemSerializer(TenantAwareSerializer):
    template_detail = RelatedFieldAlternative(
        source='template',
        read_only=True,
        serializer=BudgetTemplateSerializer
    )
    category_detail = RelatedFieldAlternative(
        source='category',
        read_only=True,
        serializer=BudgetCategorySerializer
    )

    class Meta:
        model = BudgetTemplateItem
        fields = '__all__'
        ref_name = "FinanceAPIBudgetTemplateItemSerializer"

# ============================================================================
# ACCOUNTS & REPORTS
# ============================================================================

class FinancialTransactionSerializer(TenantAwareSerializer):
    recorded_by_detail = RelatedFieldAlternative(
        source='recorded_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    
    class Meta:
        model = FinancialTransaction
        fields = '__all__'
        ref_name = "FinanceAPIFinancialTransactionSerializer"

class BankAccountSerializer(TenantAwareSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'
        ref_name = "FinanceAPIBankAccountSerializer"

class FinancialReportSerializer(TenantAwareSerializer):
    generated_by_detail = RelatedFieldAlternative(
        source='generated_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = FinancialReport
        fields = '__all__'
        ref_name = "FinanceAPIFinancialReportSerializer"
