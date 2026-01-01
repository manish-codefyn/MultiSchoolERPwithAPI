from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from apps.core.models import BaseModel
from apps.students.models import Student

class Certificate(BaseModel):
    """
    Model for managing student certificates (Migration, Transcript, etc.)
    """
    CERTIFICATE_TYPES = (
        ("MIGRATION", _("Migration Certificate")),
        ("TRANSCRIPT", _("Transcript")),
        ("CHARACTER", _("Character Certificate")),
        ("TRANSFER", _("Transfer Certificate (TC)")),
        ("BONAFIDE", _("Bonafide Certificate")),
        ("SLC", _("School Leaving Certificate")),
    )
    
    STATUS_CHOICES = (
        ("DRAFT", _("Draft")),
        ("ISSUED", _("Issued")),
        ("CANCELLED", _("Cancelled")),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name=_("Student")
    )
    certificate_type = models.CharField(
        max_length=20,
        choices=CERTIFICATE_TYPES,
        verbose_name=_("Certificate Type")
    )
    certificate_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        verbose_name=_("Certificate Number")
    )
    issue_date = models.DateField(
        default=timezone.now,
        verbose_name=_("Issue Date")
    )
    content = models.TextField(
        blank=True,
        verbose_name=_("Content/Remarks"),
        help_text=_("Additional details or manual content override")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT",
        verbose_name=_("Status")
    )
    
    class Meta:
        verbose_name = _("Certificate")
        verbose_name_plural = _("Certificates")
        ordering = ["-issue_date", "-created_at"]
        permissions = [
            ("issue_certificate", "Can issue certificates"),
            ("print_certificate", "Can print certificates"),
        ]

    def __str__(self):
        return f"{self.get_certificate_type_display()} - {self.student.full_name}"

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            self.certificate_number = self.generate_certificate_number()
        super().save(*args, **kwargs)

    def generate_certificate_number(self):
        """Generate a unique certificate number"""
        prefix = f"CERT-{timezone.now().year}-{self.certificate_type[:3]}-"
        last_cert = Certificate.objects.filter(
            certificate_number__startswith=prefix,
            tenant=self.tenant
        ).order_by('certificate_number').last()
        
        if last_cert:
            try:
                last_seq = int(last_cert.certificate_number.split('-')[-1])
                new_seq = last_seq + 1
            except ValueError:
                new_seq = 1
        else:
            new_seq = 1
            
        return f"{prefix}{new_seq:06d}"
