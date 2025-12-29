import uuid

from django.db import models

from django.conf import settings

from django.core.validators import MinValueValidator, MaxValueValidator

from django.core.exceptions import ValidationError

from django.utils import timezone

from decimal import Decimal

from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel





class FeeStructure(BaseModel):

    """

    Fee structure for different classes and programs

    """

    FEE_TYPE_CHOICES = (

        ("TUITION", _("Tuition Fee")),

        ("ADMISSION", _("Admission Fee")),

        ("EXAMINATION", _("Examination Fee")),

        ("TRANSPORT", _("Transport Fee")),

        ("HOSTEL", _("Hostel Fee")),

        ("LIBRARY", _("Library Fee")),

        ("LABORATORY", _("Laboratory Fee")),

        ("SPORTS", _("Sports Fee")),

        ("ACTIVITY", _("Activity Fee")),

        ("DEVELOPMENT", _("Development Fee")),

        ("OTHER", _("Other Fee")),

    )



    FEE_FREQUENCY_CHOICES = (

        ("ONE_TIME", _("One Time")),

        ("MONTHLY", _("Monthly")),

        ("QUARTERLY", _("Quarterly")),

        ("HALF_YEARLY", _("Half Yearly")),

        ("YEARLY", _("Yearly")),

        ("PER_TERM", _("Per Term")),

    )



    name = models.CharField(max_length=200, verbose_name=_("Fee Structure Name"))

    academic_year = models.ForeignKey(

        "academics.AcademicYear",

        on_delete=models.CASCADE,

        related_name="fee_structures",

        verbose_name=_("Academic Year")

    )

    class_name = models.ForeignKey(

        "academics.SchoolClass",

        on_delete=models.CASCADE,

        related_name="fee_structures",

        verbose_name=_("Class")

    )

    

    # Fee Configuration

    fee_type = models.CharField(

        max_length=20,

        choices=FEE_TYPE_CHOICES,

        verbose_name=_("Fee Type")

    )

    frequency = models.CharField(

        max_length=20,

        choices=FEE_FREQUENCY_CHOICES,

        verbose_name=_("Frequency")

    )

    amount = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        verbose_name=_("Amount")

    )

    

    # Due Dates

    due_day = models.PositiveIntegerField(

        validators=[MinValueValidator(1), MaxValueValidator(31)],

        verbose_name=_("Due Day of Month")

    )

    late_fee_applicable = models.BooleanField(

        default=True,

        verbose_name=_("Late Fee Applicable")

    )

    late_fee_amount = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0.00,

        verbose_name=_("Late Fee Amount")

    )

    late_fee_after_days = models.PositiveIntegerField(

        default=5,

        verbose_name=_("Late Fee After Days")

    )

    

    # Discount Configuration

    discount_allowed = models.BooleanField(

        default=False,

        verbose_name=_("Discount Allowed")

    )

    max_discount_percentage = models.DecimalField(

        max_digits=5,

        decimal_places=2,

        default=0.00,

        validators=[MinValueValidator(0), MaxValueValidator(100)],

        verbose_name=_("Maximum Discount Percentage")

    )

    

    # Status

    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))



    class Meta:

        db_table = "finance_fee_structures"

        verbose_name = _("Fee Structure")

        verbose_name_plural = _("Fee Structures")

        unique_together = [['academic_year', 'class_name', 'fee_type', 'frequency']]

        ordering = ["academic_year", "class_name", "fee_type"]

        indexes = [

            models.Index(fields=['academic_year', 'class_name']),

            models.Index(fields=['fee_type', 'is_active']),

        ]



    def __str__(self):

        return f"{self.class_name} - {self.get_fee_type_display()} - {self.academic_year}"



    @property

    def total_fee_per_year(self):

        """Calculate total fee per year based on frequency"""

        frequency_multiplier = {

            "ONE_TIME": 1,

            "MONTHLY": 12,

            "QUARTERLY": 4,

            "HALF_YEARLY": 2,

            "YEARLY": 1,

            "PER_TERM": 3,  # Assuming 3 terms per year

        }

        return self.amount * frequency_multiplier.get(self.frequency, 1)





class FeeDiscount(BaseModel):

    """

    Fee discount schemes and categories

    """

    DISCOUNT_TYPE_CHOICES = (

        ("PERCENTAGE", _("Percentage")),

        ("FIXED_AMOUNT", _("Fixed Amount")),

    )



    APPLICABLE_TO_CHOICES = (

        ("ALL_STUDENTS", _("All Students")),

        ("SPECIFIC_CLASS", _("Specific Class")),

        ("CATEGORY_BASED", _("Category Based")),

        ("MERIT_BASED", _("Merit Based")),

        ("SIBLING", _("Sibling Discount")),

        ("STAFF_CHILD", _("Staff Child")),

        ("SPECIAL_CASE", _("Special Case")),

    )

    STUDENT_CATEGORY_CHOICES = (

        ("SC", "SC"),

        ("ST", "ST"),

        ("OBC", "OBC"),

        ("GENERAL", "General"),

        ("EWS", "EWS"),

        ("MINORITY", "Minority"),

    )

    REQUIRED_DOCUMENT_CHOICES = (

    ("AADHAR", "Aadhar Card"),

    ("INCOME", "Income Certificate"),

    ("CASTE", "Caste Certificate"),

    ("DOMICILE", "Domicile Certificate"),

    ("BPL", "BPL Card"),

    ("DISABILITY", "Disability Certificate"),

)

    name = models.CharField(max_length=200, verbose_name=_("Discount Name"))

    code = models.CharField(max_length=50, unique=True, verbose_name=_("Discount Code"))

    description = models.TextField(blank=True, verbose_name=_("Description"))

    

    # Discount Configuration

    discount_type = models.CharField(

        max_length=20,

        choices=DISCOUNT_TYPE_CHOICES,

        verbose_name=_("Discount Type")

    )

    value = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        verbose_name=_("Discount Value")

    )

    applicable_to = models.CharField(

        max_length=20,

        choices=APPLICABLE_TO_CHOICES,

        verbose_name=_("Applicable To")

    )

    

    # Eligibility Criteria

    applicable_classes = models.ManyToManyField(

        "academics.SchoolClass",

        blank=True,

        related_name="fee_discounts",

        verbose_name=_("Applicable Classes")

    )

  

    min_percentage_required = models.DecimalField(

        max_digits=5,

        decimal_places=2,

        null=True,

        blank=True,

        validators=[MinValueValidator(0), MaxValueValidator(100)],

        verbose_name=_("Minimum Percentage Required")

    )

    

    # Limits

    max_discount_amount = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        null=True,

        blank=True,

        verbose_name=_("Maximum Discount Amount")

    )

    max_usage_per_student = models.PositiveIntegerField(

        default=1,

        verbose_name=_("Maximum Usage Per Student")

    )

    total_usage_limit = models.PositiveIntegerField(

        null=True,

        blank=True,

        verbose_name=_("Total Usage Limit")

    )

    

    # Validity

    valid_from = models.DateField(verbose_name=_("Valid From"))

    valid_until = models.DateField(verbose_name=_("Valid Until"))

    applicable_categories = models.CharField(

        max_length=20,

        choices=STUDENT_CATEGORY_CHOICES,

        blank=True,

        verbose_name=_("Applicable Categories")

    )

    # Documentation

    required_documents = models.CharField(

        max_length=20,

        choices=REQUIRED_DOCUMENT_CHOICES,

        blank=True,

        verbose_name=_("Required Documents")

    )



    

    # Status

    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))



    class Meta:

        db_table = "finance_fee_discounts"

        verbose_name = _("Fee Discount")

        verbose_name_plural = _("Fee Discounts")

        ordering = ["-valid_from"]

        indexes = [

            models.Index(fields=['code', 'is_active']),

            models.Index(fields=['valid_from', 'valid_until']),

        ]



    def __str__(self):

        return f"{self.name} ({self.code})"



    @property

    def is_valid(self):

        today = timezone.now().date()

        return self.valid_from <= today <= self.valid_until and self.is_active



    @property

    def usage_count(self):

        return self.applied_discounts.count()



    @property

    def remaining_usage(self):

        if self.total_usage_limit:

            return max(0, self.total_usage_limit - self.usage_count)

        return None



    def calculate_discount_amount(self, base_amount):

        """Calculate discount amount for given base amount"""

        if self.discount_type == "PERCENTAGE":

            discount_amount = (base_amount * self.value) / 100

            if self.max_discount_amount:

                discount_amount = min(discount_amount, self.max_discount_amount)

        else:  # FIXED_AMOUNT

            discount_amount = min(self.value, base_amount)

        

        return discount_amount



    def is_eligible(self, student, fee_amount):

        """Check if student is eligible for this discount"""

        if not self.is_valid:

            return False, "Discount is not valid"

        

        # Check class eligibility

        if self.applicable_to == "SPECIFIC_CLASS":

            if student.current_class not in self.applicable_classes.all():

                return False, "Student class not eligible"

        

        # Check category eligibility

        if self.applicable_to == "CATEGORY_BASED":

            if student.category not in self.applicable_categories:

                return False, "Student category not eligible"

        

        # Check merit eligibility

        if self.applicable_to == "MERIT_BASED" and self.min_percentage_required:

            if student.cumulative_grade_point < self.min_percentage_required:

                return False, "Academic performance not meeting criteria"

        

        # Check usage limits

        if self.max_usage_per_student:

            usage_count = self.applied_discounts.filter(student=student).count()

            if usage_count >= self.max_usage_per_student:

                return False, "Maximum usage limit reached for student"

        

        if self.total_usage_limit and self.usage_count >= self.total_usage_limit:

            return False, "Total usage limit reached"

        

        return True, "Eligible"





class Invoice(BaseModel):

    """

    Student fee invoices

    """

    INVOICE_STATUS_CHOICES = (

        ("DRAFT", _("Draft")),

        ("ISSUED", _("Issued")),

        ("PARTIALLY_PAID", _("Partially Paid")),

        ("PAID", _("Paid")),

        ("OVERDUE", _("Overdue")),

        ("CANCELLED", _("Cancelled")),

        ("REFUNDED", _("Refunded")),

    )



    invoice_number = models.CharField(

        max_length=50,

        unique=True,

        db_index=True,

        verbose_name=_("Invoice Number")

    )

    student = models.ForeignKey(

        "students.Student",

        on_delete=models.CASCADE,

        related_name="invoices",

        verbose_name=_("Student")

    )

    academic_year = models.ForeignKey(

        "academics.AcademicYear",

        on_delete=models.CASCADE,

        related_name="invoices",

        verbose_name=_("Academic Year")

    )

    

    # Invoice Period

    billing_period = models.CharField(max_length=100, verbose_name=_("Billing Period"))

    issue_date = models.DateField(default=timezone.localdate, verbose_name=_("Issue Date"))

    due_date = models.DateField(verbose_name=_("Due Date"))

    

    # Amounts

    subtotal = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0.00,

        verbose_name=_("Subtotal")

    )

    total_discount = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0.00,

        verbose_name=_("Total Discount")

    )

    total_tax = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0.00,

        verbose_name=_("Total Tax")

    )

    late_fee = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0.00,

        verbose_name=_("Late Fee")

    )

    total_amount = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0.00,

        verbose_name=_("Total Amount")

    )

    paid_amount = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0.00,

        verbose_name=_("Paid Amount")

    )

    due_amount = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0.00,

        verbose_name=_("Due Amount")

    )

    

    # Status

    status = models.CharField(

        max_length=20,

        choices=INVOICE_STATUS_CHOICES,

        default="DRAFT",

        verbose_name=_("Status")

    )

    

    # Payment Information

    payment_terms = models.TextField(blank=True, verbose_name=_("Payment Terms"))

    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    

    # Late Payment

    is_overdue = models.BooleanField(default=False, verbose_name=_("Is Overdue"))

    overdue_days = models.PositiveIntegerField(default=0, verbose_name=_("Overdue Days"))



    class Meta:

        db_table = "finance_invoices"

        verbose_name = _("Invoice")

        verbose_name_plural = _("Invoices")

        ordering = ["-issue_date"]

        indexes = [

            models.Index(fields=['invoice_number']),

            models.Index(fields=['student', 'status']),

            models.Index(fields=['due_date', 'status']),

            models.Index(fields=['is_overdue']),

        ]



    def __str__(self):

        return f"{self.invoice_number} - {self.student}"



    def save(self, *args, **kwargs):

        # Generate invoice number if not provided

        if not self.invoice_number:

            self.invoice_number = self.generate_invoice_number()

        

        # Calculate due amount

        self.due_amount = self.total_amount - self.paid_amount

        

        # Update status based on payment

        if self.paid_amount == 0:

            self.status = "ISSUED"

        elif self.paid_amount < self.total_amount:

            self.status = "PARTIALLY_PAID"

        elif self.paid_amount >= self.total_amount:

            self.status = "PAID"

        

        # Check overdue status

        if self.due_date < timezone.now().date() and self.due_amount > 0:

            self.is_overdue = True

            self.overdue_days = (timezone.now().date() - self.due_date).days

            if self.status != "OVERDUE":

                self.status = "OVERDUE"

        else:

            self.is_overdue = False

            self.overdue_days = 0

        

        super().save(*args, **kwargs)



    def generate_invoice_number(self):
        """Generate unique invoice number"""
        # Default prefix
        prefix = f"INV-{timezone.now().year}-"
        
        last_invoice = Invoice.objects.filter(
            invoice_number__startswith=prefix,
            tenant=self.tenant
        ).order_by('invoice_number').last()
        
        if last_invoice:
            try:
                last_num = int(last_invoice.invoice_number.split('-')[-1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1
            
        return f"{prefix}{new_num:05d}"



    @property
    def is_fully_paid(self):

        return self.paid_amount >= self.total_amount



    @property

    def payment_progress(self):

        if self.total_amount > 0:

            return (self.paid_amount / self.total_amount) * 100

        return 0



    def add_invoice_item(self, fee_structure, amount, description=""):

        """Add item to invoice"""

        InvoiceItem.objects.create(

            invoice=self,

            fee_structure=fee_structure,

            amount=amount,

            description=description

        )

        self.calculate_totals()



    def calculate_totals(self):

        """Calculate invoice totals from items"""

        items = self.items.all()

        self.subtotal = sum(item.amount for item in items)

        self.total_tax = sum(item.tax_amount for item in items)

        

        # Calculate discounts

        discount_items = self.discounts.all()

        self.total_discount = sum(item.amount for item in discount_items)

        

        # Recalculate total

        self.total_amount = self.subtotal - self.total_discount + self.total_tax + self.late_fee

        self.due_amount = self.total_amount - self.paid_amount

        

        self.save()



    def apply_discount(self, discount, applied_by, reason=""):

        """Apply discount to invoice"""

        discount_amount = discount.calculate_discount_amount(self.subtotal)

        

        AppliedDiscount.objects.create(

            invoice=self,

            discount=discount,

            amount=discount_amount,

            applied_by=applied_by,

            reason=reason

        )

        

        self.calculate_totals()



    def add_payment(self, amount, payment_method, reference, paid_by=None):

        """Add payment to invoice"""

        if amount <= 0:

            raise ValidationError(_("Payment amount must be greater than 0"))

        

        if amount > self.due_amount:

            raise ValidationError(_("Payment amount cannot exceed due amount"))

        

        # Create payment record

        payment = Payment.objects.create(

            invoice=self,

            amount=amount,

            payment_method=payment_method,

            reference_number=reference,

            paid_by=paid_by or self.student.user

        )

        

        # Update invoice paid amount

        self.paid_amount += amount

        self.save()

        

        return payment





class InvoiceItem(BaseModel):

    """

    Individual items in an invoice

    """

    invoice = models.ForeignKey(

        Invoice,

        on_delete=models.CASCADE,

        related_name="items",

        verbose_name=_("Invoice")

    )

    fee_structure = models.ForeignKey(

        FeeStructure,

        on_delete=models.CASCADE,

        related_name="invoice_items",

        verbose_name=_("Fee Structure")

    )

    amount = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        verbose_name=_("Amount")

    )

    description = models.TextField(blank=True, verbose_name=_("Description"))

    tax_amount = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0.00,

        verbose_name=_("Tax Amount")

    )



    class Meta:

        db_table = "finance_invoice_items"

        verbose_name = _("Invoice Item")

        verbose_name_plural = _("Invoice Items")



    def __str__(self):

        return f"{self.invoice} - {self.fee_structure} - {self.amount}"



    def save(self, *args, **kwargs):
        # Auto-calculate tax if not provided
        if not self.tax_amount and self.invoice.tenant:
            # Fetch active tax configuration for the tenant
            # Using global TaxConfiguration (defined later in file)
            config = TaxConfiguration.objects.filter(
                tenant=self.invoice.tenant, 
                is_active=True
            ).first()

            if config:
                self.tax_amount = round((self.amount * config.total_tax_percentage) / 100, 2)
                
        super().save(*args, **kwargs)
        
        # Update invoice totals
        self.invoice.calculate_totals()





class AppliedDiscount(BaseModel):

    """

    Discounts applied to invoices

    """

    invoice = models.ForeignKey(

        Invoice,

        on_delete=models.CASCADE,

        related_name="discounts",

        verbose_name=_("Invoice")

    )

    discount = models.ForeignKey(

        FeeDiscount,

        on_delete=models.CASCADE,

        related_name="applied_discounts",

        verbose_name=_("Discount")

    )

    amount = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        verbose_name=_("Discount Amount")

    )

    applied_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.CASCADE,

        related_name="applied_discounts",

        verbose_name=_("Applied By")

    )

    reason = models.TextField(blank=True, verbose_name=_("Reason"))

    approved_by = models.ForeignKey(

         settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="approved_discounts",

        verbose_name=_("Approved By")

    )



    class Meta:

        db_table = "finance_applied_discounts"

        verbose_name = _("Applied Discount")

        verbose_name_plural = _("Applied Discounts")



    def __str__(self):

        return f"{self.invoice} - {self.discount} - {self.amount}"





class Payment(BaseModel):

    """

    Fee payments received from students

    """

    PAYMENT_METHOD_CHOICES = (

        ("CASH", _("Cash")),

        ("CHEQUE", _("Cheque")),

        ("BANK_TRANSFER", _("Bank Transfer")),

        ("ONLINE", _("Online Payment")),

        ("DD", _("Demand Draft")),

        ("CARD", _("Credit/Debit Card")),

        ("UPI", _("UPI")),

        ("OTHER", _("Other")),

    )



    PAYMENT_STATUS_CHOICES = (

        ("PENDING", _("Pending")),

        ("COMPLETED", _("Completed")),

        ("FAILED", _("Failed")),

        ("CANCELLED", _("Cancelled")),

        ("REFUNDED", _("Refunded")),

    )



    invoice = models.ForeignKey(

        Invoice,

        on_delete=models.CASCADE,

        related_name="payments",

        verbose_name=_("Invoice")

    )

    payment_number = models.CharField(

        max_length=50,

        unique=True,

        db_index=True,

        verbose_name=_("Payment Number")

    )

    amount = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        verbose_name=_("Amount")

    )

    payment_date = models.DateTimeField(default=timezone.now, verbose_name=_("Payment Date"))

    payment_method = models.CharField(

        max_length=20,

        choices=PAYMENT_METHOD_CHOICES,

        verbose_name=_("Payment Method")

    )

    

    # Payment Details

    reference_number = models.CharField(

        max_length=100,

        blank=True,

        verbose_name=_("Reference Number")

    )

    bank_name = models.CharField(

        max_length=100,

        blank=True,

        verbose_name=_("Bank Name")

    )

    branch_name = models.CharField(

        max_length=100,

        blank=True,

        verbose_name=_("Branch Name")

    )

    cheque_dd_number = models.CharField(

        max_length=100,

        blank=True,

        verbose_name=_("Cheque/DD Number")

    )

    cheque_dd_date = models.DateField(

        null=True,

        blank=True,

        verbose_name=_("Cheque/DD Date")

    )

    

    # Online Payment Details

    transaction_id = models.CharField(

        max_length=100,

        blank=True,

        verbose_name=_("Transaction ID")

    )

    gateway_name = models.CharField(

        max_length=100,

        blank=True,

        verbose_name=_("Payment Gateway")

    )

    gateway_response = models.JSONField(

        default=dict,

        blank=True,

        verbose_name=_("Gateway Response")

    )

    

    # Status

    status = models.CharField(

        max_length=20,

        choices=PAYMENT_STATUS_CHOICES,

        default="COMPLETED",

        verbose_name=_("Status")

    )

    

    # Received By

    received_by = models.ForeignKey(

         settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="received_payments",

        verbose_name=_("Received By")

    )

    paid_by = models.ForeignKey(

         settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="made_payments",

        verbose_name=_("Paid By")

    )

    

    # Verification

    verified_by = models.ForeignKey(

         settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="verified_payments",

        verbose_name=_("Verified By")

    )

    verification_date = models.DateTimeField(

        null=True,

        blank=True,

        verbose_name=_("Verification Date")

    )

    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    student = models.ForeignKey(

        'students.Student',

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="payments",

        verbose_name=_("Student")

    )

    class Meta:

        db_table = "finance_payments"

        verbose_name = _("Payment")

        verbose_name_plural = _("Payments")

        ordering = ["-payment_date"]

        indexes = [

            models.Index(fields=['payment_number']),

            models.Index(fields=['invoice', 'status']),

            models.Index(fields=['payment_date']),

            models.Index(fields=['payment_method']),

        ]



    def __str__(self):

        return f"{self.payment_number} - {self.amount}"



    def save(self, *args, **kwargs):

        if not self.payment_number:

            self.payment_number = self.generate_payment_number()

        super().save(*args, **kwargs)



    def generate_payment_number(self):

        """Generate unique payment number"""

        prefix = f"PAY-{timezone.now().year}-{self.tenant.schema_name.upper()}-"

        last_payment = Payment.objects.filter(

            payment_number__startswith=prefix,

            tenant=self.tenant

        ).order_by('payment_number').last()

        

        if last_payment:

            last_num = int(last_payment.payment_number.split('-')[-1])

            new_num = last_num + 1

        else:

            new_num = 1

            

        return f"{prefix}{new_num:05d}"



    def verify_payment(self, user):

        """Verify payment"""

        self.verified_by = user

        self.verification_date = timezone.now()

        self.status = "COMPLETED"

        self.save()



    def mark_failed(self, reason=""):

        """Mark payment as failed"""

        self.status = "FAILED"

        self.notes = f"Failed: {reason}"

        self.save()



    def refund(self, refund_amount, reason=""):

        """Refund payment"""

        if refund_amount > self.amount:

            raise ValidationError(_("Refund amount cannot exceed payment amount"))

        

        # Create refund record

        Refund.objects.create(

            payment=self,

            amount=refund_amount,

            reason=reason,

            processed_by=self.verified_by

        )

        

        self.status = "REFUNDED"

        self.save()





class Refund(BaseModel):

    """

    Payment refunds

    """

    REFUND_STATUS_CHOICES = (

        ("REQUESTED", _("Requested")),

        ("APPROVED", _("Approved")),

        ("PROCESSED", _("Processed")),

        ("COMPLETED", _("Completed")),

        ("REJECTED", _("Rejected")),

    )



    payment = models.ForeignKey(

        Payment,

        on_delete=models.CASCADE,

        related_name="refunds",

        verbose_name=_("Payment")

    )

    refund_number = models.CharField(

        max_length=50,

        unique=True,

        db_index=True,

        verbose_name=_("Refund Number")

    )

    amount = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        verbose_name=_("Refund Amount")

    )

    reason = models.TextField(verbose_name=_("Refund Reason"))

    request_date = models.DateTimeField(default=timezone.now, verbose_name=_("Request Date"))

    status = models.CharField(

        max_length=20,

        choices=REFUND_STATUS_CHOICES,

        default="REQUESTED",

        verbose_name=_("Status")

    )

    

    # Processing

    approved_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="approved_refunds",

        verbose_name=_("Approved By")

    )

    approval_date = models.DateTimeField(

        null=True,

        blank=True,

        verbose_name=_("Approval Date")

    )

    processed_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="processed_refunds",

        verbose_name=_("Processed By")

    )

    process_date = models.DateTimeField(

        null=True,

        blank=True,

        verbose_name=_("Process Date")

    )

    completion_date = models.DateTimeField(

        null=True,

        blank=True,

        verbose_name=_("Completion Date")

    )

    

    # Bank Details for Refund

    refund_bank_account = models.CharField(

        max_length=20,

        blank=True,

        verbose_name=_("Refund Bank Account")

    )

    refund_bank_name = models.CharField(

        max_length=100,

        blank=True,

        verbose_name=_("Refund Bank Name")

    )

    refund_ifsc_code = models.CharField(

        max_length=11,

        blank=True,

        verbose_name=_("Refund IFSC Code")

    )

    

    # Rejection

    rejection_reason = models.TextField(blank=True, verbose_name=_("Rejection Reason"))



    class Meta:

        db_table = "finance_refunds"

        verbose_name = _("Refund")

        verbose_name_plural = _("Refunds")

        ordering = ["-request_date"]



    def __str__(self):

        return f"{self.refund_number} - {self.amount}"



    def save(self, *args, **kwargs):

        if not self.refund_number:

            self.refund_number = self.generate_refund_number()

        super().save(*args, **kwargs)



    def generate_refund_number(self):

        """Generate unique refund number"""

        prefix = f"REF-{timezone.now().year}-{self.tenant.schema_name.upper()}-"

        last_refund = Refund.objects.filter(

            refund_number__startswith=prefix,

            tenant=self.tenant

        ).order_by('refund_number').last()

        

        if last_refund:

            last_num = int(last_refund.refund_number.split('-')[-1])

            new_num = last_num + 1

        else:

            new_num = 1

            

        return f"{prefix}{new_num:05d}"



    def approve(self, user):

        """Approve refund"""

        self.status = "APPROVED"

        self.approved_by = user

        self.approval_date = timezone.now()

        self.save()



    def process(self, user):

        """Process refund"""

        self.status = "PROCESSED"

        self.processed_by = user

        self.process_date = timezone.now()

        self.save()



    def complete(self):

        """Mark refund as completed"""

        self.status = "COMPLETED"

        self.completion_date = timezone.now()

        self.save()



    def reject(self, user, reason):

        """Reject refund"""

        self.status = "REJECTED"

        self.approved_by = user

        self.approval_date = timezone.now()

        self.rejection_reason = reason

        self.save()





class ExpenseCategory(BaseModel):

    """

    Expense categories for school expenditures

    """

    CATEGORY_TYPE_CHOICES = (

        ("ACADEMIC", _("Academic")),

        ("ADMINISTRATIVE", _("Administrative")),

        ("INFRASTRUCTURE", _("Infrastructure")),

        ("STAFF", _("Staff Related")),

        ("UTILITY", _("Utility")),

        ("MAINTENANCE", _("Maintenance")),

        ("OTHER", _("Other")),

    )



    name = models.CharField(max_length=200, verbose_name=_("Category Name"))

    code = models.CharField(max_length=20, unique=True, verbose_name=_("Category Code"))

    category_type = models.CharField(

        max_length=20,

        choices=CATEGORY_TYPE_CHOICES,

        verbose_name=_("Category Type")

    )

    description = models.TextField(blank=True, verbose_name=_("Description"))

    parent_category = models.ForeignKey(

        'self',

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="sub_categories",

        verbose_name=_("Parent Category")

    )

    budget_amount = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0.00,

        verbose_name=_("Annual Budget Amount")

    )

    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))



    class Meta:

        db_table = "finance_expense_categories"

        verbose_name = _("Expense Category")

        verbose_name_plural = _("Expense Categories")

        ordering = ["category_type", "name"]



    def __str__(self):

        return f"{self.name} ({self.get_category_type_display()})"



    @property

    def total_expenses(self):

        current_year = timezone.now().year

        return self.expenses.filter(

            expense_date__year=current_year,

            status="APPROVED"

        ).aggregate(total=models.Sum('amount'))['total'] or 0



    @property

    def remaining_budget(self):

        return self.budget_amount - self.total_expenses



    @property

    def budget_utilization_percentage(self):

        if self.budget_amount > 0:

            return (self.total_expenses / self.budget_amount) * 100

        return 0





class Expense(BaseModel):

    """

    School expenses and expenditures

    """

    EXPENSE_STATUS_CHOICES = (

        ("DRAFT", _("Draft")),

        ("SUBMITTED", _("Submitted")),

        ("APPROVED", _("Approved")),

        ("REJECTED", _("Rejected")),

        ("PAID", _("Paid")),

    )



    PAYMENT_METHOD_CHOICES = (

        ("CASH", _("Cash")),

        ("CHEQUE", _("Cheque")),

        ("BANK_TRANSFER", _("Bank Transfer")),

        ("ONLINE", _("Online Transfer")),

        ("OTHER", _("Other")),

    )

    SUPPORTING_DOCUMENT_CHOICES = (

        ("BILL", _("Bill")),

        ("INVOICE", _("Invoice")),

        ("RECEIPT", _("Receipt")),

        ("VOUCHER", _("Payment Voucher")),

        ("QUOTATION", _("Quotation")),

        ("OTHER", _("Other")),

    )

    expense_number = models.CharField(

        max_length=50,

        unique=True,

        db_index=True,

        verbose_name=_("Expense Number")

    )

    category = models.ForeignKey(

        ExpenseCategory,

        on_delete=models.CASCADE,

        related_name="expenses",

        verbose_name=_("Expense Category")

    )

    title = models.CharField(max_length=200, verbose_name=_("Expense Title"))

    description = models.TextField(verbose_name=_("Description"))

    

    # Amount and Dates

    amount = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        verbose_name=_("Amount")

    )

    expense_date = models.DateField(default=timezone.localdate, verbose_name=_("Expense Date"))

    payment_date = models.DateField(

        null=True,

        blank=True,

        verbose_name=_("Payment Date")

    )

    

    # Vendor Information

    vendor_name = models.CharField(max_length=200, verbose_name=_("Vendor Name"))

    vendor_contact = models.CharField(

        max_length=100,

        blank=True,

        verbose_name=_("Vendor Contact")

    )

    bill_number = models.CharField(

        max_length=100,

        blank=True,

        verbose_name=_("Bill Number")

    )

    bill_date = models.DateField(

        null=True,

        blank=True,

        verbose_name=_("Bill Date")

    )

    

    # Payment Information

    payment_method = models.CharField(

        max_length=20,

        choices=PAYMENT_METHOD_CHOICES,

        verbose_name=_("Payment Method")

    )

    reference_number = models.CharField(

        max_length=100,

        blank=True,

        verbose_name=_("Reference Number")

    )

    

    # Status and Approval

    status = models.CharField(

        max_length=20,

        choices=EXPENSE_STATUS_CHOICES,

        default="DRAFT",

        verbose_name=_("Status")

    )

    submitted_by = models.ForeignKey(

         settings.AUTH_USER_MODEL,

        on_delete=models.CASCADE,

        related_name="submitted_expenses",

        verbose_name=_("Submitted By")

    )

    approved_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="approved_expenses",

        verbose_name=_("Approved By")

    )

    approval_date = models.DateTimeField(

        null=True,

        blank=True,

        verbose_name=_("Approval Date")

    )

    rejection_reason = models.TextField(blank=True, verbose_name=_("Rejection Reason"))

    

    # Documents

    supporting_documents = models.CharField(

        max_length=30,

        choices=SUPPORTING_DOCUMENT_CHOICES,

        blank=True,

        null=True,

        verbose_name=_("Supporting Document")

    )

    class Meta:

        db_table = "finance_expenses"

        verbose_name = _("Expense")

        verbose_name_plural = _("Expenses")

        ordering = ["-expense_date"]

        indexes = [

            models.Index(fields=['expense_number']),

            models.Index(fields=['category', 'status']),

            models.Index(fields=['expense_date']),

        ]



    def __str__(self):

        return f"{self.expense_number} - {self.title} - {self.amount}"



    def save(self, *args, **kwargs):

        if not self.expense_number:

            self.expense_number = self.generate_expense_number()

        super().save(*args, **kwargs)



    def generate_expense_number(self):

        """Generate unique expense number"""

        prefix = f"EXP-{timezone.now().year}-{self.tenant.schema_name.upper()}-"

        last_expense = Expense.objects.filter(

            expense_number__startswith=prefix,

            tenant=self.tenant

        ).order_by('expense_number').last()

        

        if last_expense:

            last_num = int(last_expense.expense_number.split('-')[-1])

            new_num = last_num + 1

        else:

            new_num = 1

            

        return f"{prefix}{new_num:05d}"



    def submit_for_approval(self):

        """Submit expense for approval"""

        self.status = "SUBMITTED"

        self.save()



    def approve(self, user):

        """Approve expense"""

        self.status = "APPROVED"

        self.approved_by = user

        self.approval_date = timezone.now()

        self.save()



    def reject(self, user, reason):

        """Reject expense"""

        self.status = "REJECTED"

        self.approved_by = user

        self.approval_date = timezone.now()

        self.rejection_reason = reason

        self.save()



    def mark_paid(self, payment_date=None):

        """Mark expense as paid"""

        self.status = "PAID"

        self.payment_date = payment_date or timezone.now().date()

        self.save()



class Budget(BaseModel):

    """

    Annual budget planning with user-friendly inputs

    """

    

    # Budget status constants

    STATUS_DRAFT = "DRAFT"

    STATUS_SUBMITTED = "SUBMITTED"

    STATUS_APPROVED = "APPROVED"

    STATUS_ACTIVE = "ACTIVE"

    STATUS_CLOSED = "CLOSED"

    

    BUDGET_STATUS_CHOICES = (

        (STATUS_DRAFT, _("📝 Draft")),

        (STATUS_SUBMITTED, _("📤 Submitted for Approval")),

        (STATUS_APPROVED, _("✅ Approved")),

        (STATUS_ACTIVE, _("▶️ Active")),

        (STATUS_CLOSED, _("🔒 Closed")),

    )

    

    # Budget types

    BUDGET_TYPES = [

        ("ACADEMIC", _("Academic Budget")),

        ("OPERATIONAL", _("Operational Budget")),

        ("DEVELOPMENT", _("Development Budget")),

        ("SPECIAL", _("Special Projects Budget")),

        ("ANNUAL", _("Annual Budget")),

    ]

    

    # Basic Information

    name = models.CharField(

        max_length=200, 

        verbose_name=_("Budget Name"),

        help_text=_("Enter a descriptive name (e.g., 'Academic Year 2024-25 Operating Budget')")

    )

    

    budget_type = models.CharField(

        max_length=20,

        choices=BUDGET_TYPES,

        default="ANNUAL",

        verbose_name=_("Budget Type"),

        help_text=_("Select the type of budget")

    )

    

    academic_year = models.ForeignKey(

        "academics.AcademicYear",

        on_delete=models.CASCADE,

        related_name="budgets",

        verbose_name=_("Academic Year"),

        help_text=_("Select the academic year this budget applies to")

    )

    

    # Financial Information

    total_amount = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        verbose_name=_("Total Budget Amount"),

        help_text=_("Total allocated budget amount in ₹"),

        validators=[MinValueValidator(Decimal('0.01'))]

    )

    

    status = models.CharField(

        max_length=20,

        choices=BUDGET_STATUS_CHOICES,

        default=STATUS_DRAFT,

        verbose_name=_("Status"),

        help_text=_("Current status of the budget")

    )

    

    # Budget Period

    start_date = models.DateField(

        verbose_name=_("Start Date"),

        help_text=_("Budget start date (format: YYYY-MM-DD)")

    )

    

    end_date = models.DateField(

        verbose_name=_("End Date"),

        help_text=_("Budget end date (format: YYYY-MM-DD)")

    )

    

    # Approval Information

    prepared_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.CASCADE,

        related_name="prepared_budgets",

        verbose_name=_("Prepared By"),

        help_text=_("User who created this budget")

    )

    

    approved_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="approved_budgets",

        verbose_name=_("Approved By"),

        help_text=_("User who approved this budget")

    )

    

    approval_date = models.DateTimeField(

        null=True,

        blank=True,

        verbose_name=_("Approval Date"),

        help_text=_("Date when budget was approved")

    )

    

    # Notes

    notes = models.TextField(

        blank=True, 

        verbose_name=_("Notes"),

        help_text=_("Additional notes or comments about this budget")

    )

    

    # Audit fields

   

    last_reviewed = models.DateTimeField(null=True, blank=True, verbose_name=_("Last Reviewed"))

    

    class Meta:

        db_table = "finance_budgets"

        verbose_name = _("Budget")

        verbose_name_plural = _("Budgets")

        unique_together = [['academic_year', 'name']]

        ordering = ["-academic_year", "name"]

        permissions = [

            ("can_approve_budget", "Can approve budgets"),

            ("can_activate_budget", "Can activate budgets"),

            ("can_submit_budget", "Can submit budgets for approval"),

        ]



    def __str__(self):

        return f"{self.name} - {self.academic_year}"

    

    # Helper Properties

    @property

    def is_status_active(self):

        """Check if budget is currently active"""

        return self.status == self.STATUS_ACTIVE

    

    @property

    def can_edit(self):

        """Check if budget can be edited"""

        return self.status in [self.STATUS_DRAFT, self.STATUS_SUBMITTED]

    

    @property

    def duration_days(self):

        """Get budget duration in days"""

        return (self.end_date - self.start_date).days

    

    @property

    def days_remaining(self):

        """Get days remaining in budget period"""

        today = timezone.now().date()

        if today > self.end_date:

            return 0

        return (self.end_date - today).days

    

    @property

    def total_expenses(self):

        """Calculate total expenses from budget items"""

        # Sum of all expenses from budget items

        total = self.budget_items.filter(expense_record__isnull=False).aggregate(

            total=models.Sum('expense_record__amount')

        )['total'] or 0

        return Decimal(total)

    

    @property

    def remaining_budget(self):

        """Calculate remaining budget"""

        return self.total_amount - self.total_expenses

    

    @property

    def utilization_percentage(self):

        """Calculate budget utilization percentage"""

        if self.total_amount > 0:

            return (self.total_expenses / self.total_amount) * 100

        return 0

    

    def activate(self):

        """Activate the budget"""

        # Deactivate other active budgets for the same academic year

        Budget.objects.filter(

            academic_year=self.academic_year,

            status=self.STATUS_ACTIVE

        ).update(status=self.STATUS_CLOSED)

        

        self.status = self.STATUS_ACTIVE

        self.save(update_fields=['status'])

    

    def submit_for_approval(self, user):

        """Submit budget for approval"""

        if self.status == self.STATUS_DRAFT:

            self.status = self.STATUS_SUBMITTED

            self.save(update_fields=['status'])

            return True

        return False

    

    def approve(self, user):

        """Approve the budget"""

        if self.status in [self.STATUS_SUBMITTED, self.STATUS_DRAFT]:

            self.status = self.STATUS_APPROVED

            self.approved_by = user

            self.approval_date = timezone.now()

            self.save(update_fields=['status', 'approved_by', 'approval_date'])

            return True

        return False





class BudgetCategory(BaseModel):

    """

    Budget categories for organizing budget items

    """

    CATEGORY_TYPES = [

        ("INCOME", _("Income")),

        ("EXPENSE", _("Expense")),

        ("CAPITAL", _("Capital Expenditure")),

        ("REVENUE", _("Revenue Expenditure")),

    ]

    

    name = models.CharField(

        max_length=100,

        verbose_name=_("Category Name"),

        help_text=_("Enter category name (e.g., 'Salaries', 'Infrastructure')")

    )

    

    code = models.CharField(

        max_length=20,

        unique=True,

        verbose_name=_("Category Code"),

        help_text=_("Short code for category (e.g., 'SAL', 'INFRA')")

    )

    

    category_type = models.CharField(

        max_length=20,

        choices=CATEGORY_TYPES,

        default="EXPENSE",

        verbose_name=_("Category Type"),

        help_text=_("Type of budget category")

    )

    

    description = models.TextField(

        blank=True,

        verbose_name=_("Description"),

        help_text=_("Description of what this category includes")

    )

    

    parent_category = models.ForeignKey(

        'self',

        on_delete=models.CASCADE,

        null=True,

        blank=True,

        related_name="sub_categories",

        verbose_name=_("Parent Category"),

        help_text=_("Select parent category if this is a sub-category")

    )

    

    is_active = models.BooleanField(

        default=True,

        verbose_name=_("Is Active"),

        help_text=_("Uncheck to deactivate this category")

    )

    

    display_order = models.PositiveIntegerField(

        default=0,

        verbose_name=_("Display Order"),

        help_text=_("Order in which categories appear in lists")

    )

    

    class Meta:

        db_table = "finance_budget_categories"

        verbose_name = _("Budget Category")

        verbose_name_plural = _("Budget Categories")

        ordering = ["display_order", "name"]

    

    def __str__(self):

        return f"{self.name} ({self.code})"





class BudgetItem(BaseModel):

    """

    Individual budget item - user-friendly alternative to JSON field

    """

    budget = models.ForeignKey(

        Budget,

        on_delete=models.CASCADE,

        related_name="budget_items",

        verbose_name=_("Budget"),

        help_text=_("Select the budget this item belongs to")

    )

    

    category = models.ForeignKey(

        BudgetCategory,

        on_delete=models.PROTECT,

        related_name="budget_items",

        verbose_name=_("Category"),

        help_text=_("Select budget category for this item")

    )

    

    description = models.CharField(

        max_length=500,

        verbose_name=_("Description"),

        help_text=_("Detailed description of this budget item")

    )

    

    allocated_amount = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        validators=[MinValueValidator(Decimal('0.01'))],

        verbose_name=_("Allocated Amount"),

        help_text=_("Amount allocated for this item in ₹")

    )

    

    # Monthly breakdown (optional)

    january = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

        validators=[MinValueValidator(Decimal('0.00'))],

        verbose_name=_("January"),

        help_text=_("Amount allocated for January")

    )

    

    february = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

        validators=[MinValueValidator(Decimal('0.00'))],

        verbose_name=_("February")

    )

    

    march = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

        validators=[MinValueValidator(Decimal('0.00'))],

        verbose_name=_("March")

    )

    

    april = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

        validators=[MinValueValidator(Decimal('0.00'))],

        verbose_name=_("April")

    )

    

    may = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

        validators=[MinValueValidator(Decimal('0.00'))],

        verbose_name=_("May")

    )

    

    june = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

        validators=[MinValueValidator(Decimal('0.00'))],

        verbose_name=_("June")

    )

    

    july = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

        validators=[MinValueValidator(Decimal('0.00'))],

        verbose_name=_("July")

    )

    

    august = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

        validators=[MinValueValidator(Decimal('0.00'))],

        verbose_name=_("August")

    )

    

    september = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

        validators=[MinValueValidator(Decimal('0.00'))],

        verbose_name=_("September")

    )

    

    october = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

        validators=[MinValueValidator(Decimal('0.00'))],

        verbose_name=_("October")

    )

    

    november = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

        validators=[MinValueValidator(Decimal('0.00'))],

        verbose_name=_("November")

    )

    

    december = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0,

        validators=[MinValueValidator(Decimal('0.00'))],

        verbose_name=_("December")

    )

    

    # Additional fields

    is_fixed = models.BooleanField(

        default=False,

        verbose_name=_("Is Fixed Cost"),

        help_text=_("Check if this is a fixed/regular cost")

    )

    

    is_discretionary = models.BooleanField(

        default=False,

        verbose_name=_("Is Discretionary"),

        help_text=_("Check if this expense is discretionary/optional")

    )

    

    priority = models.IntegerField(

        choices=[(1, "High"), (2, "Medium"), (3, "Low")],

        default=2,

        verbose_name=_("Priority"),

        help_text=_("Priority level for this budget item")

    )

    

    notes = models.TextField(

        blank=True,

        verbose_name=_("Notes"),

        help_text=_("Additional notes about this budget item")

    )

    

    # For tracking actual expenses

    expense_record = models.ForeignKey(

        'finance.Expense',

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="budget_items",

        verbose_name=_("Expense Record"),

        help_text=_("Link to actual expense record if applicable")

    )

    

    # Display order

    display_order = models.PositiveIntegerField(

        default=0,

        verbose_name=_("Display Order")

    )

    

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    

    class Meta:

        db_table = "finance_budget_items"

        verbose_name = _("Budget Item")

        verbose_name_plural = _("Budget Items")

        ordering = ["display_order", "category__name"]

    

    def __str__(self):

        return f"{self.category.name} - {self.description[:50]}"

    

    # Helper properties

    @property

    def monthly_allocations(self):

        """Get monthly allocations as a dictionary"""

        return {

            'january': float(self.january),

            'february': float(self.february),

            'march': float(self.march),

            'april': float(self.april),

            'may': float(self.may),

            'june': float(self.june),

            'july': float(self.july),

            'august': float(self.august),

            'september': float(self.september),

            'october': float(self.october),

            'november': float(self.november),

            'december': float(self.december),

        }

    

    @property

    def total_monthly_allocations(self):

        """Sum of all monthly allocations"""

        monthly = self.monthly_allocations.values()

        return sum(monthly)

    

    @property

    def remaining_amount(self):

        """Calculate remaining amount after expenses"""

        if self.expense_record:

            spent = self.expense_record.amount

        else:

            spent = Decimal('0.00')

        return self.allocated_amount - spent

    

    @property

    def spent_amount(self):

        """Get amount spent on this item"""

        if self.expense_record:

            return self.expense_record.amount

        return Decimal('0.00')

    

    @property

    def utilization_percentage(self):

        """Calculate percentage of allocated amount spent"""

        if self.allocated_amount > 0:

            return (self.spent_amount / self.allocated_amount) * 100

        return 0

    

    def get_allocation_for_month(self, month_name):

        """Get allocation for specific month"""

        month_name = month_name.lower()

        return getattr(self, month_name, Decimal('0.00'))





class BudgetTemplate(BaseModel):

    """

    Predefined budget templates for easy budget creation

    """

    name = models.CharField(

        max_length=200,

        verbose_name=_("Template Name"),

        help_text=_("Name of the budget template")

    )

    

    description = models.TextField(

        blank=True,

        verbose_name=_("Description"),

        help_text=_("Description of when to use this template")

    )

    

    budget_type = models.CharField(

        max_length=20,

        choices=Budget.BUDGET_TYPES,

        verbose_name=_("Budget Type")

    )

    

    template_items = models.ManyToManyField(

        'finance.BudgetItem',

        related_name='template_items',

        verbose_name=_("Template Items"),

        help_text=_("Items to include in this template")

    )

    

    is_active = models.BooleanField(default=True)



    

    class Meta:

        db_table = "finance_budget_templates"

        verbose_name = _("Budget Template")

        verbose_name_plural = _("Budget Templates")

    

    def __str__(self):

        return self.name

    

    def create_budget_from_template(self, budget_name, academic_year, prepared_by):

        """Create a new budget from this template"""

        from django.db import transaction

        

        with transaction.atomic():

            # Create budget

            budget = Budget.objects.create(

                name=budget_name,

                academic_year=academic_year,

                prepared_by=prepared_by,

                budget_type=self.budget_type,

                start_date=academic_year.start_date,

                end_date=academic_year.end_date,

                total_amount=Decimal('0.00')  # Will be updated

            )

            

            total_amount = Decimal('0.00')

            

            # Create budget items from template

            for template_item in self.template_items.all():

                budget_item = BudgetItem.objects.create(

                    budget=budget,

                    category=template_item.category,

                    description=template_item.description,

                    allocated_amount=template_item.default_amount,

                    is_fixed=template_item.is_fixed,

                    is_discretionary=template_item.is_discretionary,

                    priority=template_item.priority,

                )

                total_amount += template_item.default_amount

            

            # Update budget total

            budget.total_amount = total_amount

            budget.save()

            

            return budget





class BudgetTemplateItem(BaseModel):

    """

    Item in a budget template

    """

    category = models.ForeignKey(

        BudgetCategory,

        on_delete=models.CASCADE,

        verbose_name=_("Category")

    )



    template = models.ForeignKey(

        BudgetTemplate,

        on_delete=models.CASCADE,

        related_name="items",

        verbose_name=_("Template"),

        null=True,  # Initially null until we migrate existing data or recreate schema

        blank=True

    )

    

    description = models.CharField(

        max_length=500,

        verbose_name=_("Description")

    )

    

    default_amount = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        verbose_name=_("Default Amount"),

        help_text=_("Default amount for this item in templates")

    )

    

    is_fixed = models.BooleanField(default=False)

    is_discretionary = models.BooleanField(default=False)

    priority = models.IntegerField(choices=[(1, "High"), (2, "Medium"), (3, "Low")], default=2)

    

    class Meta:

        db_table = "finance_budget_template_items"

        verbose_name = _("Budget Template Item")

        verbose_name_plural = _("Budget Template Items")

    

    def __str__(self):

        return f"{self.category.name}: {self.description}"





class FinancialTransaction(BaseModel):

    """

    General financial transactions

    """

    TRANSACTION_TYPE_CHOICES = (

        ("RECEIPT", _("Receipt")),

        ("PAYMENT", _("Payment")),

        ("JOURNAL", _("Journal Entry")),

        ("CONTRA", _("Contra Entry")),

    )



    transaction_number = models.CharField(

        max_length=50,

        unique=True,

        db_index=True,

        verbose_name=_("Transaction Number")

    )

    transaction_type = models.CharField(

        max_length=20,

        choices=TRANSACTION_TYPE_CHOICES,

        verbose_name=_("Transaction Type")

    )

    transaction_date = models.DateField(default=timezone.localdate, verbose_name=_("Transaction Date"))

    amount = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        verbose_name=_("Amount")

    )

    

    # Accounts

    debit_account = models.CharField(max_length=100, verbose_name=_("Debit Account"))

    credit_account = models.CharField(max_length=100, verbose_name=_("Credit Account"))

    

    # Description

    description = models.TextField(verbose_name=_("Description"))

    reference = models.CharField(

        max_length=100,

        blank=True,

        verbose_name=_("Reference")

    )

    

    # Related Documents

    related_invoice = models.ForeignKey(

        Invoice,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="transactions",

        verbose_name=_("Related Invoice")

    )

    related_expense = models.ForeignKey(

        Expense,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="transactions",

        verbose_name=_("Related Expense")

    )

    

    # Entry By

    entered_by = models.ForeignKey(

         settings.AUTH_USER_MODEL,

        on_delete=models.CASCADE,

        related_name="entered_transactions",

        verbose_name=_("Entered By")

    )

    verified_by = models.ForeignKey(

         settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="verified_transactions",

        verbose_name=_("Verified By")

    )



    class Meta:

        db_table = "finance_transactions"

        verbose_name = _("Financial Transaction")

        verbose_name_plural = _("Financial Transactions")

        ordering = ["-transaction_date"]

        indexes = [

            models.Index(fields=['transaction_number']),

            models.Index(fields=['transaction_date', 'transaction_type']),

        ]



    def __str__(self):

        return f"{self.transaction_number} - {self.transaction_type} - {self.amount}"



    def save(self, *args, **kwargs):

        if not self.transaction_number:

            self.transaction_number = self.generate_transaction_number()

        super().save(*args, **kwargs)



    def generate_transaction_number(self):

        """Generate unique transaction number"""

        prefix = f"TRN-{timezone.now().year}-{self.tenant.schema_name.upper()}-"

        last_transaction = FinancialTransaction.objects.filter(

            transaction_number__startswith=prefix,

            tenant=self.tenant

        ).order_by('transaction_number').last()

        

        if last_transaction:

            last_num = int(last_transaction.transaction_number.split('-')[-1])

            new_num = last_num + 1

        else:

            new_num = 1

        return f"{prefix}{new_num:05d}"

class BankAccount(BaseModel):

    """

    School bank accounts management

    """

    ACCOUNT_TYPE_CHOICES = (

        ("SAVINGS", _("Savings Account")),

        ("CURRENT", _("Current Account")),

        ("FIXED_DEPOSIT", _("Fixed Deposit")),

        ("RECURRING_DEPOSIT", _("Recurring Deposit")),

    )


    account_name = models.CharField(max_length=200, verbose_name=_("Account Name"))

    account_number = models.CharField(

        max_length=20,

        unique=True,

        verbose_name=_("Account Number")

    )

    bank_name = models.CharField(max_length=100, verbose_name=_("Bank Name"))

    branch_name = models.CharField(max_length=100, verbose_name=_("Branch Name"))

    ifsc_code = models.CharField(max_length=11, verbose_name=_("IFSC Code"))

    account_type = models.CharField(

        max_length=20,

        choices=ACCOUNT_TYPE_CHOICES,

        verbose_name=_("Account Type")

    )

    

    # Balance Information

    current_balance = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0.00,

        verbose_name=_("Current Balance")

    )

    as_of_date = models.DateField(default=timezone.localdate, verbose_name=_("Balance As Of"))

    

    # Contact Information

    bank_contact = models.CharField(

        max_length=100,

        blank=True,

        verbose_name=_("Bank Contact")

    )

    bank_address = models.TextField(blank=True, verbose_name=_("Bank Address"))

    

    # Authorization

    authorized_signatories = models.ManyToManyField(

         settings.AUTH_USER_MODEL,

        blank=True,

        related_name="authorized_bank_accounts",

        verbose_name=_("Authorized Signatories")

    )

    

    # Status

    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))



    class Meta:

        db_table = "finance_bank_accounts"

        verbose_name = _("Bank Account")

        verbose_name_plural = _("Bank Accounts")

        ordering = ["bank_name", "account_number"]



    def __str__(self):

        return f"{self.bank_name} - {self.account_number} - {self.account_name}"



    def update_balance(self, new_balance, as_of_date=None):

        """Update account balance"""

        self.current_balance = new_balance

        self.as_of_date = as_of_date or timezone.now().date()

        self.save()





class FinancialReport(BaseModel):

    """

    Financial reports and statements

    """

    REPORT_TYPE_CHOICES = (

        ("INCOME_STATEMENT", _("Income Statement")),

        ("BALANCE_SHEET", _("Balance Sheet")),

        ("CASH_FLOW", _("Cash Flow Statement")),

        ("FEE_COLLECTION", _("Fee Collection Report")),

        ("EXPENSE_SUMMARY", _("Expense Summary Report")),

        ("BUDGET_VS_ACTUAL", _("Budget vs Actual Report")),

        ("DUE_FEES", _("Due Fees Report")),

        ("TAX_REPORT", _("Tax Report")),

    )



    PERIOD_CHOICES = (

        ("DAILY", _("Daily")),

        ("WEEKLY", _("Weekly")),

        ("MONTHLY", _("Monthly")),

        ("QUARTERLY", _("Quarterly")),

        ("YEARLY", _("Yearly")),

        ("CUSTOM", _("Custom Period")),

    )



    report_type = models.CharField(

        max_length=20,

        choices=REPORT_TYPE_CHOICES,

        verbose_name=_("Report Type")

    )

    report_name = models.CharField(max_length=200, verbose_name=_("Report Name"))

    period = models.CharField(

        max_length=20,

        choices=PERIOD_CHOICES,

        verbose_name=_("Report Period")

    )

    start_date = models.DateField(verbose_name=_("Start Date"))

    end_date = models.DateField(verbose_name=_("End Date"))

    

    # Report Data

    report_data = models.JSONField(

        default=dict,

        verbose_name=_("Report Data")

    )

    summary = models.JSONField(

        default=dict,

        verbose_name=_("Report Summary")

    )

    

    # Generation Info

    generated_by = models.ForeignKey(

         settings.AUTH_USER_MODEL,

        on_delete=models.CASCADE,

        related_name="generated_reports",

        verbose_name=_("Generated By")

    )

    generated_at = models.DateTimeField(default=timezone.now, verbose_name=_("Generated At"))

    

    # File Export

    export_file = models.FileField(

        upload_to='financial_reports/',

        null=True,

        blank=True,

        verbose_name=_("Export File")

    )

    export_format = models.CharField(

        max_length=10,

        choices=(

            ("PDF", "PDF"),

            ("EXCEL", "Excel"),

            ("CSV", "CSV"),

        ),

        blank=True,

        verbose_name=_("Export Format")

    )



    class Meta:

        db_table = "finance_reports"

        verbose_name = _("Financial Report")

        verbose_name_plural = _("Financial Reports")

        ordering = ["-generated_at"]



    def __str__(self):

        return f"{self.report_name} - {self.start_date} to {self.end_date}"


class TaxConfiguration(BaseModel):
    """
    Tax configuration including GST details
    """
    TAX_TYPE_CHOICES = (
        ("GST", _("GST")),
        ("VAT", _("VAT")),
        ("OTHER", _("Other")),
    )
    
    tax_name = models.CharField(max_length=50, default="GST", verbose_name=_("Tax Name"))
    tax_number = models.CharField(max_length=50, blank=True, verbose_name=_("Tax Number (GSTIN/VAT)"))
    
    # Tax Components
    cgst_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name=_("CGST %")
    )
    sgst_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name=_("SGST %")
    )
    igst_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name=_("IGST %")
    )
    
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    
    class Meta:
        db_table = "finance_tax_configuration"
        verbose_name = _("Tax Configuration")
        verbose_name_plural = _("Tax Configuration")
        
    def __str__(self):
        return f"{self.tax_name} - {self.tax_number}"
        
    @property
    def total_tax_percentage(self):
        return self.cgst_percentage + self.sgst_percentage + self.igst_percentage

