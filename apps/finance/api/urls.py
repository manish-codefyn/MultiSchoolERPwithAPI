from django.urls import path
from .views import (
    FeeStructureListCreateAPIView, FeeStructureDetailAPIView,
    FeeDiscountListCreateAPIView, FeeDiscountDetailAPIView,
    InvoiceListCreateAPIView, InvoiceDetailAPIView,
    InvoiceItemListCreateAPIView, InvoiceItemDetailAPIView,
    AppliedDiscountListCreateAPIView, AppliedDiscountDetailAPIView,
    PaymentListCreateAPIView, PaymentDetailAPIView,
    RefundListCreateAPIView, RefundDetailAPIView,
    ExpenseCategoryListCreateAPIView, ExpenseCategoryDetailAPIView,
    ExpenseListCreateAPIView, ExpenseDetailAPIView,
    BudgetListCreateAPIView, BudgetDetailAPIView,
    BudgetCategoryListCreateAPIView, BudgetCategoryDetailAPIView,
    BudgetItemListCreateAPIView, BudgetItemDetailAPIView,
    BudgetTemplateListCreateAPIView, BudgetTemplateDetailAPIView,
    BudgetTemplateItemListCreateAPIView, BudgetTemplateItemDetailAPIView,
    FinancialTransactionListCreateAPIView, FinancialTransactionDetailAPIView,
    BankAccountListCreateAPIView, BankAccountDetailAPIView,
    FinancialReportListCreateAPIView, FinancialReportDetailAPIView
)
from .dashboard_view import FinanceDashboardAPIView

urlpatterns = [
    # Dashboard
    path('dashboard/', FinanceDashboardAPIView.as_view(), name='dashboard'),

    # Fee Structure
    path('fee-structures/', FeeStructureListCreateAPIView.as_view(), name='fee-structure-list'),
    path('fee-structures/<uuid:pk>/', FeeStructureDetailAPIView.as_view(), name='fee-structure-detail'),

    # Fee Discount
    path('fee-discounts/', FeeDiscountListCreateAPIView.as_view(), name='fee-discount-list'),
    path('fee-discounts/<uuid:pk>/', FeeDiscountDetailAPIView.as_view(), name='fee-discount-detail'),

    # Invoice
    path('invoices/', InvoiceListCreateAPIView.as_view(), name='invoice-list'),
    path('invoices/<uuid:pk>/', InvoiceDetailAPIView.as_view(), name='invoice-detail'),

    # Invoice Item
    path('invoice-items/', InvoiceItemListCreateAPIView.as_view(), name='invoice-item-list'),
    path('invoice-items/<uuid:pk>/', InvoiceItemDetailAPIView.as_view(), name='invoice-item-detail'),

    # Applied Discount
    path('applied-discounts/', AppliedDiscountListCreateAPIView.as_view(), name='applied-discount-list'),
    path('applied-discounts/<uuid:pk>/', AppliedDiscountDetailAPIView.as_view(), name='applied-discount-detail'),

    # Payment
    path('payments/', PaymentListCreateAPIView.as_view(), name='payment-list'),
    path('payments/<uuid:pk>/', PaymentDetailAPIView.as_view(), name='payment-detail'),

    # Refund
    path('refunds/', RefundListCreateAPIView.as_view(), name='refund-list'),
    path('refunds/<uuid:pk>/', RefundDetailAPIView.as_view(), name='refund-detail'),

    # Expense Category
    path('expense-categories/', ExpenseCategoryListCreateAPIView.as_view(), name='expense-category-list'),
    path('expense-categories/<uuid:pk>/', ExpenseCategoryDetailAPIView.as_view(), name='expense-category-detail'),

    # Expense
    path('expenses/', ExpenseListCreateAPIView.as_view(), name='expense-list'),
    path('expenses/<uuid:pk>/', ExpenseDetailAPIView.as_view(), name='expense-detail'),

    # Budget
    path('budgets/', BudgetListCreateAPIView.as_view(), name='budget-list'),
    path('budgets/<uuid:pk>/', BudgetDetailAPIView.as_view(), name='budget-detail'),

    # Budget Category
    path('budget-categories/', BudgetCategoryListCreateAPIView.as_view(), name='budget-category-list'),
    path('budget-categories/<uuid:pk>/', BudgetCategoryDetailAPIView.as_view(), name='budget-category-detail'),

    # Budget Item
    path('budget-items/', BudgetItemListCreateAPIView.as_view(), name='budget-item-list'),
    path('budget-items/<uuid:pk>/', BudgetItemDetailAPIView.as_view(), name='budget-item-detail'),

    # Budget Template
    path('budget-templates/', BudgetTemplateListCreateAPIView.as_view(), name='budget-template-list'),
    path('budget-templates/<uuid:pk>/', BudgetTemplateDetailAPIView.as_view(), name='budget-template-detail'),

    # Budget Template Item
    path('budget-template-items/', BudgetTemplateItemListCreateAPIView.as_view(), name='budget-template-item-list'),
    path('budget-template-items/<uuid:pk>/', BudgetTemplateItemDetailAPIView.as_view(), name='budget-template-item-detail'),

    # Financial Transaction
    path('transactions/', FinancialTransactionListCreateAPIView.as_view(), name='financial-transaction-list'),
    path('transactions/<uuid:pk>/', FinancialTransactionDetailAPIView.as_view(), name='financial-transaction-detail'),

    # Bank Account
    path('bank-accounts/', BankAccountListCreateAPIView.as_view(), name='bank-account-list'),
    path('bank-accounts/<uuid:pk>/', BankAccountDetailAPIView.as_view(), name='bank-account-detail'),

    # Financial Report
    path('financial-reports/', FinancialReportListCreateAPIView.as_view(), name='financial-report-list'),
    path('financial-reports/<uuid:pk>/', FinancialReportDetailAPIView.as_view(), name='financial-report-detail'),
]
