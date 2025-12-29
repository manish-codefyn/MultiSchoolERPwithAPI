
        # Verify Signature
        if RazorpayService.verify_payment_signature(payment_id, order_id, signature, tenant=request.tenant):
            try:
                # 1. Fetch Order to get Notes (Invoice ID)
                client = RazorpayService.get_client(tenant=request.tenant)
                order = client.order.fetch(order_id)
                notes = order.get('notes', {})
                invoice_id = notes.get('invoice_id')
                
                if not invoice_id:
                     raise Exception("Invoice ID not found in payment notes")

                # 2. Get Invoice
                invoice = Invoice.objects.get(pk=invoice_id)
                
                # 3. Create Payment Record (Avoid duplicates)
                if not Payment.objects.filter(transaction_id=payment_id).exists():
                    payment = Payment.objects.create(
                        invoice=invoice,
                        student=invoice.student,
                        amount=invoice.due_amount, # Or fetch exact amount from payment
                        payment_date=timezone.now().date(),
                        payment_method='Razorpay',
                        transaction_id=payment_id,
                        status='COMPLETED', 
                        remarks=f"Razorpay Order: {order_id}"
                    )
                    
                    # 4. Update Invoice Status (Handled by signals usually, but let's ensure)
                    # invoice.calculate_totals() # Should trigger status update
                    
                    messages.success(request, f"Payment of {payment.amount} received successfully!")
                else:
                    messages.info(request, "Payment already recorded.")
                    
                return redirect('student_portal:invoice_details', pk=invoice_id)
                
            except Exception as e:
                logger.error(f"Callback Error: {e}")
                messages.error(request, "Payment verified but failed to record locally. Please contact support.")
                return redirect('student_portal:invoice_list')
