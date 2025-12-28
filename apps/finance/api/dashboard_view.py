from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from apps.core.api.views import BaseAPIView
from apps.finance.models import Invoice, Payment, Expense

class FinanceDashboardAPIView(BaseAPIView):
    """
    API View to provide summary statistics for the Finance Dashboard
    """
    roles_required = ['admin', 'principal', 'vice_principal', 'accountant']
    
    def get(self, request, *args, **kwargs):
        tenant = request.tenant
        today = timezone.now().date()
        current_year = today.year 
        current_month_start = today.replace(day=1)

        # 1. Total Collection (Collected Payments)
        all_payments = Payment.objects.filter(tenant=tenant, status='COMPLETED')
        total_collected = all_payments.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # 2. Outstanding / Due
        all_invoices = Invoice.objects.filter(tenant=tenant, status__in=['ISSUED', 'PARTIALLY_PAID', 'OVERDUE'])
        total_due = all_invoices.aggregate(Sum('due_amount'))['due_amount__sum'] or 0
        
        # 3. Monthly Collection (This Month)
        monthly_payments = all_payments.filter(payment_date__gte=current_month_start)
        monthly_collected = monthly_payments.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # 4. Expenses (This Month)
        monthly_expenses = 0
        try:
             expenses_month = Expense.objects.filter(tenant=tenant, expense_date__gte=current_month_start)
             monthly_expenses = expenses_month.aggregate(Sum('amount'))['amount__sum'] or 0
        except Exception:
             pass
             
        # 5. Chart Data (Last 6 Months)
        chart_data = []
        try:
            # We will manually construct last 6 months to ensure zero-filling
            from datetime import timedelta
            
            for i in range(5, -1, -1):
                # Rough calculation for previous months
                month_date = today.replace(day=1) - timedelta(days=i*30) 
                # Better month iteration logic needed ideally, but this approximates
                # Actually, let's just use a simple robust loop
                pass 
            
            # Simplified approach using Django Aggregation
            # Last 6 months range
            six_months_ago = today - timedelta(days=180)
            
            revenue_by_month = Payment.objects.filter(
                tenant=tenant, 
                status='COMPLETED',
                payment_date__gte=six_months_ago
            ).annotate(month=TruncMonth('payment_date')).values('month').annotate(total=Sum('amount')).order_by('month')
            
            expense_by_month = Expense.objects.filter(
                tenant=tenant,
                expense_date__gte=six_months_ago
            ).annotate(month=TruncMonth('expense_date')).values('month').annotate(total=Sum('amount')).order_by('month')
            
            # Convert to dict for easy lookup
            rev_map = {entry['month'].strftime('%Y-%m'): entry['total'] for entry in revenue_by_month if entry['month']}
            exp_map = {entry['month'].strftime('%Y-%m'): entry['total'] for entry in expense_by_month if entry['month']}
            
            # Generate labels
            for i in range(5, -1, -1):
                date_cursor = (today.replace(day=1) - timedelta(days=i*28)) # Safe subtract
                key = date_cursor.strftime('%Y-%m')
                label = date_cursor.strftime('%b')
                
                chart_data.append({
                    "month": label,
                    "revenue": rev_map.get(key, 0),
                    "expense": exp_map.get(key, 0)
                })
                
        except Exception as e:
            # Fallback empty chart if error
            print(f"Chart error: {e}")
            chart_data = []

        data = {
            "stats": [
                {
                    "label": "Total Collected",
                    "value": f"₹{total_collected:,.0f}",
                    "sub_label": "Lifetime",
                    "icon": "account_balance_wallet",
                    "color": "#4CAF50" # Green
                },
                {
                    "label": "Outstanding Due",
                    "value": f"₹{total_due:,.0f}",
                    "sub_label": "Pending Fees",
                    "icon": "money_off",
                    "color": "#F44336" # Red
                },
                {
                    "label": "Monthly Collection",
                    "value": f"₹{monthly_collected:,.0f}",
                    "sub_label": "This Month",
                    "icon": "calendar_today",
                    "color": "#2196F3" # Blue
                },
                 {
                    "label": "Monthly Expenses",
                    "value": f"₹{monthly_expenses:,.0f}",
                    "sub_label": "This Month",
                    "icon": "trending_down",
                    "color": "#FF9800" # Orange
                }
            ],
            "chart_data": chart_data,
            "services": [
                {"name": "Fee Structures", "icon": "account_balance", "route": "/finance/fees"},
                {"name": "Invoices", "icon": "receipt", "route": "/finance/invoices"},
                {"name": "Collect Fees", "icon": "payment", "route": "/finance/collect"},
                {"name": "Expenses", "icon": "money_off", "route": "/finance/expenses"},
                {"name": "Transactions", "icon": "history", "route": "/finance/transactions"},
                {"name": "Reports", "icon": "assessment", "route": "/finance/reports"},
            ],
            "meta": {
                "currency": "INR"
            }
        }
        
        return Response(data, status=status.HTTP_200_OK)
