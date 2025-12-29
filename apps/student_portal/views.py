from django.views.generic import TemplateView, ListView, DetailView, View
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from apps.communications.models import MessageThread, Message


from apps.core.views import BaseView
from apps.students.models import Student
from apps.finance.models import Invoice, Payment
from apps.finance.services import RazorpayService
from apps.assignments.models import Assignment, Submission
from apps.academics.models import TimeTable, Subject
from apps.exams.models import ExamResult
from apps.communications.models import MessageThread, Message

class StudentPortalBaseView(BaseView):
    """Base view for student portal ensuring user is a student"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        # Allow parents if they are implemented, for now assume simple student role check or profile existence
        if request.user.role != 'student' and not request.user.is_superuser: 
             # You might want to allow parents here too
             pass
        return super().dispatch(request, *args, **kwargs)

    def get_student(self):
        """Helper to get student profile"""
        if hasattr(self.request.user, 'student_profile'):
            return self.request.user.student_profile
        return None

class StudentDashboardView(StudentPortalBaseView, TemplateView):
    template_name = 'student_portal/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_student()
        if not student:
            return context

        # 1. Attendance Summary (Placeholder logic - replace with actual aggregation if efficient)
        # context['attendance_percentage'] = student.attendance_records.aggregate(...)
        
        # 2. Financial Summary
        unpaid_invoices = Invoice.objects.filter(student=student, status__in=['ISSUED', 'PARTIALLY_PAID', 'OVERDUE'])
        context['pending_fees'] = unpaid_invoices.aggregate(Sum('due_amount'))['due_amount__sum'] or 0
        context['pending_invoice_count'] = unpaid_invoices.count()

        # 3. Upcoming Assignments
        context['upcoming_assignments'] = Assignment.objects.filter(
            class_name=student.current_class,
            due_date__gte=timezone.now(),
            status='PUBLISHED'
        ).exclude(
            submissions__student=student
        ).order_by('due_date')[:5]

        # 4. Recent Results (if exams app is ready)
        # context['recent_results'] = ExamResult.objects.filter(student=student).order_by('-created_at')[:5]

        return context


class PortalAssignmentListView(StudentPortalBaseView, TemplateView):
    """Student view for their assignments"""
    template_name = 'student_portal/academics/assignments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_student()
        if not student:
            return context

        # Get all assignments for student's class
        all_assignments = Assignment.objects.filter(
            class_name=student.current_class,
            status='PUBLISHED'
        ).filter(
            Q(section__isnull=True) | Q(section=student.section)
        ).select_related('subject', 'class_name', 'section').order_by('-due_date')

        # Get student's submissions
        submitted_ids = Submission.objects.filter(
            student=student
        ).values_list('assignment_id', flat=True)

        # Categorize assignments
        now = timezone.now()
        pending = []
        submitted = []
        overdue = []

        for assignment in all_assignments:
            if assignment.id in submitted_ids:
                # Get submission details
                assignment.submission = Submission.objects.filter(
                    assignment=assignment, student=student
                ).first()
                submitted.append(assignment)
            elif assignment.due_date < now:
                overdue.append(assignment)
            else:
                pending.append(assignment)

        context['pending_assignments'] = pending
        context['submitted_assignments'] = submitted
        context['overdue_assignments'] = overdue
        context['total_count'] = len(all_assignments)
        context['pending_count'] = len(pending)
        context['submitted_count'] = len(submitted)
        context['overdue_count'] = len(overdue)

        return context


class PortalAssignmentDetailView(StudentPortalBaseView, DetailView):
    """View assignment details and submit"""
    model = Assignment
    template_name = 'student_portal/academics/assignment_detail.html'
    context_object_name = 'assignment'

    def get_queryset(self):
        student = self.get_student()
        if not student:
            return Assignment.objects.none()
        return Assignment.objects.filter(
            class_name=student.current_class,
            status='PUBLISHED'
        ).filter(
            Q(section__isnull=True) | Q(section=student.section)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_student()
        if student:
            context['submission'] = Submission.objects.filter(
                assignment=self.object, student=student
            ).first()
            context['can_submit'] = self.object.due_date >= timezone.now() or not context['submission']
        return context


class PortalAssignmentSubmitView(StudentPortalBaseView, View):
    """Handle assignment submission"""

    def post(self, request, pk):
        student = self.get_student()
        if not student:
            messages.error(request, "Student profile not found.")
            return redirect('student_portal:assignments')

        assignment = get_object_or_404(Assignment, pk=pk)

        # Check if already submitted
        existing = Submission.objects.filter(assignment=assignment, student=student).first()
        if existing:
            messages.warning(request, "You have already submitted this assignment.")
            return redirect('student_portal:assignment_detail', pk=pk)

        # Create submission
        submission_text = request.POST.get('submission_text', '')
        submission_file = request.FILES.get('submission_file')

        submission = Submission.objects.create(
            tenant=request.tenant,
            assignment=assignment,
            student=student,
            submission_text=submission_text,
            submission_file=submission_file
        )

        messages.success(request, "Assignment submitted successfully!")
        return redirect('student_portal:assignment_detail', pk=pk)


# ==================== FINANCIALS ====================

class PortalInvoiceListView(StudentPortalBaseView, ListView):
    model = Invoice
    template_name = 'student_portal/finance/invoice_list.html'
    context_object_name = 'invoices'

    def get_queryset(self):
        student = self.get_student()
        if not student:
            return Invoice.objects.none()
        return Invoice.objects.filter(student=student).order_by('-issue_date')


class PortalPaymentInitiateView(StudentPortalBaseView, View):
    """Create Razorpay Order and show payment page"""
    
    def get(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk, student=self.get_student())
        
        if invoice.due_amount <= 0:
            messages.info(request, "This invoice is already paid.")
            return redirect('student_portal:invoice_list')

        # Create Razorpay Order
        try:
            order = RazorpayService.create_order(
                amount=invoice.due_amount, 
                currency="INR", 
                receipt=str(invoice.invoice_number),
                notes={'invoice_id': str(invoice.pk), 'student_id': str(invoice.student.pk)},
                tenant=request.tenant
            )
        except Exception as e:
            import traceback
            traceback.print_exc() # Print to console for server logs
            messages.error(request, f"Failed to initiate payment gateway: {str(e)}")
            return redirect('student_portal:invoice_list')

        if not order:
            messages.error(request, "Failed to initiate payment gateway. Please try again.")
            return redirect('student_portal:invoice_list')

        # Get Key ID for frontend
        razorpay_key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
        try:
            from apps.tenants.models import PaymentConfiguration
            pc = PaymentConfiguration.objects.get(tenant=request.tenant)
            if pc.razorpay_key_id:
                razorpay_key_id = pc.razorpay_key_id
        except Exception:
            pass

        context = {
            'invoice': invoice,
            'razorpay_order_id': order['id'],
            'razorpay_key_id': razorpay_key_id,
            'amount': invoice.due_amount,
            'amount_paise': int(invoice.due_amount * 100), # Razorpay expects paise
            'currency': 'INR',
            'callback_url': request.build_absolute_uri(reverse_lazy('student_portal:payment_callback')),
            'student': self.get_student() # For pre-filling email/contact
        }
        return render(request, 'student_portal/finance/payment_confirm.html', context)


class PortalDirectPaymentInitiateView(StudentPortalBaseView, View):
    template_name = 'student_portal/finance/direct_payment.html'

    def get(self, request):
        student = self.get_student()
        if not student:
            messages.error(request, "Student profile not found.")
            return redirect('student_portal:dashboard')

        from apps.finance.models import FeeStructure
        
        # Filter active fees for this tenant
        fees = FeeStructure.objects.filter(
            tenant=request.tenant,
            is_active=True
        )
        
        context = {
            'fee_structures': fees
        }
        return render(request, self.template_name, context)

    def post(self, request):
        student = self.get_student()
        if not student:
            return redirect('student_portal:dashboard')

        fee_structure_id = request.POST.get('fee_structure')
        if not fee_structure_id:
            messages.error(request, "Please select a fee type.")
            return redirect('student_portal:direct_payment')

        try:
            from apps.finance.models import FeeStructure, Invoice, InvoiceItem
            from apps.academics.models import AcademicYear
            
            fee_structure = get_object_or_404(FeeStructure, pk=fee_structure_id, tenant=request.tenant)

            # Get current academic year
            academic_year = AcademicYear.objects.filter(tenant=request.tenant, is_current=True).first()
            if not academic_year:
                # Fallback to any latest year or return error
                academic_year = AcademicYear.objects.filter(tenant=request.tenant).order_by('-start_date').first()
                if not academic_year:
                     messages.error(request, "No active academic year found for this tenant.")
                     return redirect('student_portal:direct_payment')

            # Create Invoice
            invoice = Invoice.objects.create(
                tenant=request.tenant,
                student=student,
                academic_year=academic_year,
                issue_date=timezone.now().date(),
                due_date=timezone.now().date(), # Due immediately
                billing_period=f"Immediate Payment - {timezone.now().strftime('%B %Y')}",
                created_by=request.user 
            )

            # Add Item
            invoice.add_invoice_item(
                fee_structure=fee_structure,
                amount=fee_structure.amount,
                description=fee_structure.name
            )
            
            invoice.save()
            
            messages.success(request, "Invoice created. Proceeding to payment...")
            return redirect('student_portal:pay_invoice', pk=invoice.pk)

        except Exception as e:
            messages.error(request, f"Error creating invoice: {str(e)}")
            return redirect('student_portal:direct_payment')


@method_decorator(csrf_exempt, name='dispatch')
class PortalPaymentCallbackView(View):
    """Handle Razorpay Callback"""

    def post(self, request):
        data = request.POST
        payment_id = data.get('razorpay_payment_id', '')
        order_id = data.get('razorpay_order_id', '')
        signature = data.get('razorpay_signature', '')

        if not all([payment_id, order_id, signature]):
             messages.error(request, "Invalid payment response received.")
             return redirect('student_portal:invoice_list')

        # Verify Signature
        # Verify Signature
        if RazorpayService.verify_payment_signature(payment_id, order_id, signature, tenant=request.tenant):
            try:
                # 1. Fetch Order to get Notes (Invoice ID)
                client = RazorpayService.get_client(tenant=request.tenant)
                order = client.order.fetch(order_id)
                notes = order.get('notes', {})
                invoice_id = notes.get('invoice_id')
                
                if not invoice_id:
                     # Fallback: simple redirect if no invoice context (shouldn't happen with our initiate view)
                     messages.warning(request, "Payment verified but invoice context missing.")
                     return redirect('student_portal:invoice_list')

                # 2. Get Invoice & Create Payment
                # We import here to avoid circular dependencies if any
                from apps.finance.models import Invoice, Payment
                from django.utils import timezone
                
                invoice = get_object_or_404(Invoice, pk=invoice_id)
                
                # Check duplication
                if not Payment.objects.filter(transaction_id=payment_id).exists():
                    # Calculate amount from order (paise to main unit)
                    amount_paid = float(order['amount']) / 100
                    
                    Payment.objects.create(
                        tenant=request.tenant,
                        invoice=invoice,
                        student=invoice.student,
                        amount=amount_paid,
                        payment_date=timezone.now().date(),
                        payment_method='ONLINE', # Must be one of CHOICES
                        gateway_name='Razorpay',
                        gateway_response=order,
                        transaction_id=payment_id,
                        status='COMPLETED', 
                        notes=f"Razorpay Order: {order_id}"
                    )
                    
                    # Update Invoice Status
                    invoice.paid_amount += Decimal(str(amount_paid))
                    invoice.save()
                    
                    messages.success(request, f"Payment of {amount_paid} received successfully!")
                else:
                    messages.info(request, "Payment already recorded.")
                    
                return redirect('student_portal:invoice_list')
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                messages.error(request, f"Payment verified but failed to record locally: {str(e)}")
                return redirect('student_portal:invoice_list')
            
        else:
            messages.error(request, "Payment verification failed.")
            return redirect('student_portal:invoice_list')


# ==================== ACADEMICS ====================

class PortalTimetableView(StudentPortalBaseView, TemplateView):
    template_name = 'student_portal/academics/timetable.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_student()
        if student and student.current_class:
            # Fetch timetable entries
            queryset = TimeTable.objects.filter(
                class_name=student.current_class
            )
            
            # Filter by section (either global for class or specific to section)
            queryset = queryset.filter(
                Q(section__isnull=True) | Q(section=student.section)
            )
            
            # Filter by academic year (Crucial fix)
            if student.academic_year:
                queryset = queryset.filter(academic_year=student.academic_year)
            
            context['timetable_entries'] = queryset.select_related(
                'subject', 'subject__subject', 'teacher', 'class_name', 'section'
            ).order_by('day', 'start_time')
            
        return context

# ==================== GAMES & EXTRAS ====================

class PortalGamesView(StudentPortalBaseView, TemplateView):
    template_name = 'student_portal/games/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mock data for games
        context['mind_games'] = [
            {'name': 'Memory Match', 'url': reverse_lazy('student_portal:games_memory'), 'icon': 'brain', 'color': 'primary'},
            {'name': 'Tic Tac Toe', 'url': reverse_lazy('student_portal:games_tictactoe'), 'icon': 'grid', 'color': 'success'},
            {'name': 'Puzzle Master', 'url': '#', 'icon': 'extension', 'color': 'warning'},
        ]
        context['knowledge_games'] = [
            {'name': 'Math Quiz', 'url': reverse_lazy('student_portal:games_quiz'), 'icon': 'calculator', 'color': 'info'},
            {'name': 'Science Trivia', 'url': '#', 'icon': 'bulb', 'color': 'danger'},
            {'name': 'History Quest', 'url': '#', 'icon': 'time', 'color': 'secondary'},
        ]

        return context

class MemoryGameView(StudentPortalBaseView, TemplateView):
    template_name = 'student_portal/games/memory.html'

class MathQuizView(StudentPortalBaseView, TemplateView):
    template_name = 'student_portal/games/quiz.html'

class TicTacToeView(StudentPortalBaseView, TemplateView):
    template_name = 'student_portal/games/tictactoe.html'


class StudentProfileView(StudentPortalBaseView, DetailView):
    template_name = 'student_portal/profile.html'
    context_object_name = 'student'

    def get_object(self):
        return self.get_student()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        if student:
            context['guardians'] = student.guardians.all()
            context['addresses'] = student.addresses.all()
        return context



# ==================== COMMUNICATIONS ====================



class PortalInboxView(StudentPortalBaseView, ListView):

    model = MessageThread

    template_name = 'student_portal/communications/inbox.html'

    context_object_name = 'threads'

    

    def get_queryset(self):

        user = self.request.user

        return MessageThread.objects.filter(

            participants=user, 

            is_active=True

        ).prefetch_related('participants', 'messages').distinct().order_by('-last_message_at')



class PortalThreadDetailView(StudentPortalBaseView, DetailView):

    model = MessageThread

    template_name = 'student_portal/communications/thread_detail.html'

    context_object_name = 'thread'



    def get_object(self):

        obj = super().get_object()

        # Security check: User must be participant

        if self.request.user not in obj.participants.all():

            from django.core.exceptions import PermissionDenied

            raise PermissionDenied

        return obj



    def post(self, request, *args, **kwargs):

        thread = self.get_object()

        body = request.POST.get('body')

        

        if body:

            message = Message.objects.create(

                thread=thread,

                sender=request.user,

                body=body,

                message_type='MESSAGE',

                subject=f"Re: {thread.title}"

            )

            # Update thread last message

            thread.last_message_at = timezone.now()

            thread.save()

            

            # TODO: Send Real-time notification to other participants?

            # Implemented simplified broadcast via channel layer if consumer supports it.

            # But focusing on saving for now.



        return redirect('student_portal:thread_detail', pk=thread.pk)


class PortalInvoicePrintView(StudentPortalBaseView, DetailView):
    model = Invoice
    template_name = 'student_portal/finance/invoice_print.html'
    context_object_name = 'invoice'

    def get_object(self):
        obj = super().get_object()
        # Security: Only own invoices
        if obj.student.user != self.request.user and not self.request.user.is_superuser:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return obj
