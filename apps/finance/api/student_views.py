from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.finance.models import Invoice, Payment
from apps.finance.api.serializers import InvoiceSerializer, PaymentSerializer
from apps.finance.services import RazorpayService

class IsStudent(permissions.BasePermission):
    """
    Allows access only to students.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'STUDENT'

class StudentInvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        # Filter for current student's invoices
        user = self.request.user
        return Invoice.objects.filter(student__user=user).select_related('academic_year', 'student').order_by('-issue_date')

    @action(detail=True, methods=['post'], url_path='initiate-payment')
    def initiate_payment(self, request, pk=None):
        """
        Creates a Razorpay Order for the invoice
        """
        invoice = self.get_object()
        
        if invoice.status in ['PAID', 'CANCELLED', 'REFUNDED']:
             return Response({"error": "Invoice is already paid or cancelled"}, status=status.HTTP_400_BAD_REQUEST)

        amount_to_pay = invoice.due_amount
        if amount_to_pay <= 0:
             return Response({"error": "No amount due"}, status=status.HTTP_400_BAD_REQUEST)

        # Create Order
        order = RazorpayService.create_order(
            amount=amount_to_pay,
            currency="INR",
            receipt=invoice.invoice_number,
            notes={
                'invoice_id': str(invoice.id),
                'student_id': str(invoice.student.id)
            }
        )

        if not order:
            return Response({"error": "Failed to create payment order"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "success": True,
            "order_id": order['id'],
            "amount": amount_to_pay,
            "currency": "INR",
            "key_id": RazorpayService.get_client().auth[0] if RazorpayService.get_client() else "",
            "invoice_number": invoice.invoice_number
        })

    @action(detail=True, methods=['post'], url_path='verify-payment')
    def verify_payment(self, request, pk=None):
        """
        Verifies Razorpay payment signature and updates invoice
        """
        invoice = self.get_object()
        
        payment_id = request.data.get('razorpay_payment_id')
        order_id = request.data.get('razorpay_order_id')
        signature = request.data.get('razorpay_signature')

        if not all([payment_id, order_id, signature]):
            return Response({"error": "Missing payment details"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify Signature
        is_valid = RazorpayService.verify_payment_signature(payment_id, order_id, signature)
        
        if is_valid:
            # 1. Create Payment Record
            # We assume full amount paid for simplicity, or fetch from order
            # Ideally fetch amount from Razorpay, but trusting Invoice due amount for now as order was created for it
            
            # Check if payment already exists
            if Payment.objects.filter(transaction_id=payment_id).exists():
                 return Response({"success": True, "message": "Payment already recorded"})

            payment = invoice.add_payment(
                amount=invoice.due_amount,
                payment_method='ONLINE',
                reference=payment_id, # transaction ID
                paid_by=request.user
            )
            
            # Update Payment details
            payment.transaction_id = payment_id
            payment.gateway_name = "Razorpay"
            payment.gateway_response = request.data
            payment.status = "COMPLETED"
            payment.save()

            return Response({
                "success": True, 
                "message": "Payment successful",
                "invoice_status": invoice.status,
                "download_url": f"/api/v1/finance/invoices/{invoice.id}/download/" # Placeholder
            })
        else:
            return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)
