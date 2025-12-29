from rest_framework import status
from apps.core.api.views import (
    BaseListCreateAPIView, BaseRetrieveUpdateDestroyAPIView
)
from apps.finance.models import (
    FeeStructure, FeeDiscount, Invoice, InvoiceItem, AppliedDiscount,
    Payment, Refund, ExpenseCategory, Expense, Budget, BudgetCategory,
    BudgetItem, BudgetTemplate, BudgetTemplateItem, FinancialTransaction,
    BankAccount, FinancialReport, TaxConfiguration
)
from .serializers import (
    FeeStructureSerializer, FeeDiscountSerializer, InvoiceSerializer,
    InvoiceItemSerializer, AppliedDiscountSerializer, PaymentSerializer,
    RefundSerializer, ExpenseCategorySerializer, ExpenseSerializer,
    BudgetSerializer, BudgetCategorySerializer, BudgetItemSerializer,
    BudgetTemplateSerializer, BudgetTemplateItemSerializer,
    FinancialTransactionSerializer, BankAccountSerializer,
    FinancialReportSerializer
)

# FeeStructure
class FeeStructureListCreateAPIView(BaseListCreateAPIView):
    model = FeeStructure
    serializer_class = FeeStructureSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

class FeeStructureDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = FeeStructure
    serializer_class = FeeStructureSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

# FeeDiscount
class FeeDiscountListCreateAPIView(BaseListCreateAPIView):
    model = FeeDiscount
    serializer_class = FeeDiscountSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

class FeeDiscountDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = FeeDiscount
    serializer_class = FeeDiscountSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

# Invoice
class InvoiceListCreateAPIView(BaseListCreateAPIView):
    model = Invoice
    serializer_class = InvoiceSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

class InvoiceDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Invoice
    serializer_class = InvoiceSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

# InvoiceItem
class InvoiceItemListCreateAPIView(BaseListCreateAPIView):
    model = InvoiceItem
    serializer_class = InvoiceItemSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

class InvoiceItemDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = InvoiceItem
    serializer_class = InvoiceItemSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

# AppliedDiscount
class AppliedDiscountListCreateAPIView(BaseListCreateAPIView):
    model = AppliedDiscount
    serializer_class = AppliedDiscountSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

class AppliedDiscountDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = AppliedDiscount
    serializer_class = AppliedDiscountSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

# Payment
class PaymentListCreateAPIView(BaseListCreateAPIView):
    model = Payment
    serializer_class = PaymentSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

class PaymentDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Payment
    serializer_class = PaymentSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

# Refund
class RefundListCreateAPIView(BaseListCreateAPIView):
    model = Refund
    serializer_class = RefundSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

class RefundDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Refund
    serializer_class = RefundSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

# ExpenseCategory
class ExpenseCategoryListCreateAPIView(BaseListCreateAPIView):
    model = ExpenseCategory
    serializer_class = ExpenseCategorySerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

class ExpenseCategoryDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = ExpenseCategory
    serializer_class = ExpenseCategorySerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

# Expense
class ExpenseListCreateAPIView(BaseListCreateAPIView):
    model = Expense
    serializer_class = ExpenseSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

class ExpenseDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Expense
    serializer_class = ExpenseSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

# Budget
class BudgetListCreateAPIView(BaseListCreateAPIView):
    model = Budget
    serializer_class = BudgetSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

class BudgetDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Budget
    serializer_class = BudgetSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

# BudgetCategory
class BudgetCategoryListCreateAPIView(BaseListCreateAPIView):
    model = BudgetCategory
    serializer_class = BudgetCategorySerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

class BudgetCategoryDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = BudgetCategory
    serializer_class = BudgetCategorySerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

# BudgetItem
class BudgetItemListCreateAPIView(BaseListCreateAPIView):
    model = BudgetItem
    serializer_class = BudgetItemSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

class BudgetItemDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = BudgetItem
    serializer_class = BudgetItemSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

# BudgetTemplate
class BudgetTemplateListCreateAPIView(BaseListCreateAPIView):
    model = BudgetTemplate
    serializer_class = BudgetTemplateSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

class BudgetTemplateDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = BudgetTemplate
    serializer_class = BudgetTemplateSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

# BudgetTemplateItem
class BudgetTemplateItemListCreateAPIView(BaseListCreateAPIView):
    model = BudgetTemplateItem
    serializer_class = BudgetTemplateItemSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

class BudgetTemplateItemDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = BudgetTemplateItem
    serializer_class = BudgetTemplateItemSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

# FinancialTransaction
class FinancialTransactionListCreateAPIView(BaseListCreateAPIView):
    model = FinancialTransaction
    serializer_class = FinancialTransactionSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

class FinancialTransactionDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = FinancialTransaction
    serializer_class = FinancialTransactionSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

# BankAccount
class BankAccountListCreateAPIView(BaseListCreateAPIView):
    model = BankAccount
    serializer_class = BankAccountSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

class BankAccountDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = BankAccount
    serializer_class = BankAccountSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

# FinancialReport
class FinancialReportListCreateAPIView(BaseListCreateAPIView):
    model = FinancialReport
    serializer_class = FinancialReportSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']

class FinancialReportDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = FinancialReport
    serializer_class = FinancialReportSerializer
    roles_required = ['ACCOUNTANT', 'ADMIN']
