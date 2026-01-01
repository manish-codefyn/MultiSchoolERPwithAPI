from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import FormView
from apps.core.views import BaseListView, BaseCreateView, BaseDetailView, BaseUpdateView, BaseDeleteView, BaseView
from apps.certificates.models import Certificate
from apps.certificates.forms import CertificateForm, BulkCertificateForm
from apps.students.models import Student
import io
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings

class CertificateListView(BaseListView):
    """List all certificates"""
    model = Certificate
    template_name = 'certificates/certificate_list.html'
    context_object_name = 'certificates'
    ordering = ['-issue_date']
    search_fields = ['student__first_name', 'student__last_name', 'certificate_number', 'student__admission_number']
    permission_required = 'certificates.view_certificate'
    roles_required = ['admin', 'principal', 'registrar']

class CertificateCreateView(BaseCreateView):
    """Create a new certificate"""
    model = Certificate
    form_class = CertificateForm
    template_name = 'certificates/certificate_form.html'
    permission_required = 'certificates.add_certificate'
    roles_required = ['admin', 'principal', 'registrar']
    success_url = reverse_lazy('certificates:certificate_list')

class CertificateDetailView(BaseDetailView):
    """View certificate details / Print View"""
    model = Certificate
    template_name = 'certificates/certificate_detail.html'
    context_object_name = 'certificate'
    permission_required = 'certificates.view_certificate'
    roles_required = ['admin', 'principal', 'registrar', 'student', 'parent']

class CertificateUpdateView(BaseUpdateView):
    """Update certificate"""
    model = Certificate
    form_class = CertificateForm
    template_name = 'certificates/certificate_form.html'
    permission_required = 'certificates.change_certificate'
    roles_required = ['admin', 'principal', 'registrar']
    success_url = reverse_lazy('certificates:certificate_list')

class CertificateDeleteView(BaseDeleteView):
    """Delete certificate"""
    model = Certificate
    template_name = 'certificates/certificate_confirm_delete.html'
    success_url = reverse_lazy('certificates:certificate_list')
    permission_required = 'certificates.delete_certificate'
    roles_required = ['admin', 'principal']

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import Paragraph, Frame, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import io
import os
from django.conf import settings

class CertificateDownloadView(BaseDetailView):
    """Download certificate as PDF using ReportLab"""
    model = Certificate
    permission_required = 'certificates.view_certificate'
    roles_required = ['admin', 'principal', 'registrar', 'student', 'parent']

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Draw Border
        p.setStrokeColor(colors.black)
        p.setLineWidth(3)
        p.rect(20, 20, width - 40, height - 40)
        
        p.setStrokeColor(colors.darkgrey)
        p.setLineWidth(1)
        p.rect(25, 25, width - 50, height - 50)

        # Draw Header (School Name)
        tenant_name = self.object.tenant.name if self.object.tenant else "SCHOOL NAME"
        
        # Logo Logic
        try:
            if self.object.tenant and hasattr(self.object.tenant, 'configuration') and self.object.tenant.configuration.logo:
                logo_path = self.object.tenant.configuration.logo.path
                if os.path.exists(logo_path):
                    # Draw logo centered above name or to the left
                    # Let's put it top center
                    p.drawImage(logo_path, width/2.0 - 0.75*inch, height - 1.8*inch, width=1.5*inch, height=1.5*inch, mask='auto', preserveAspectRatio=True)
                    text_y_start = height - 2*inch
                else:
                    text_y_start = height - 1*inch
            else:
                 text_y_start = height - 1*inch
        except Exception:
            text_y_start = height - 1*inch

        p.setFont("Helvetica-Bold", 30)
        p.drawCentredString(width / 2.0, text_y_start, tenant_name)
        
        # Address and Affiliation
        p.setFont("Helvetica", 10)
        details_y = text_y_start - 0.25*inch
        
        address_str = ""
        if self.object.tenant:
             # Fix for 'TenantAddress' object has no attribute 'decode'
             # Assuming address might be an object or string. Stringify it safely.
             address_val = getattr(self.object.tenant, 'address', '')
             address_str = str(address_val) if address_val else ""
             
        if address_str:
             p.drawCentredString(width / 2.0, details_y, address_str)
             details_y -= 0.2*inch
             
        # School Code and Affiliation
        if self.object.tenant and hasattr(self.object.tenant, 'configuration'):
            config = self.object.tenant.configuration
            affiliation_text = []
            if config.affiliation_number:
                affiliation_text.append(f"Affiliation No: {config.affiliation_number}")
            if config.school_code:
                affiliation_text.append(f"School Code: {config.school_code}")
            
            if affiliation_text:
                p.setFont("Helvetica-Bold", 10)
                p.drawCentredString(width / 2.0, details_y, " | ".join(affiliation_text))

        
        # Certificate Title
        p.setFont("Helvetica-Bold", 24)
        p.drawCentredString(width / 2.0, height - 3.5*inch, self.object.get_certificate_type_display().upper())
        
        # Content body
        
        # Content body
        # Using Platypus for wrapped text
        styles = getSampleStyleSheet()
        style_body = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=14,
            leading=24,
            alignment=TA_CENTER
        )
        
        if self.object.content:
            text_content = self.object.content.replace('\n', '<br/>')
        else:
            # Fallback default content
            # Get parent/guardian name
            parent_name = "Guardian"
            father = self.object.student.guardians.filter(relation='FATHER').first()
            if father:
                parent_name = father.full_name
            else:
                mother = self.object.student.guardians.filter(relation='MOTHER').first()
                if mother:
                    parent_name = mother.full_name
                else:
                    guardian = self.object.student.guardians.filter(is_primary=True).first()
                    if guardian:
                        parent_name = guardian.full_name

            text_content = (
                f"This is to certify that <b>{self.object.student.full_name}</b> "
                f"(Admission No: <b>{self.object.student.admission_number}</b>), "
                f"son/daughter of <b>{parent_name}</b>, "
                f"was a bona fide student of this institution."
                f"<br/><br/>"
                f"He/She bears a good moral character and has satisfactorily completed the requirements."
                f"<br/><br/>"
                f"We wish him/her success in all future endeavors."
            )

        paragraph = Paragraph(text_content, style_body)
        
        # Frame for text
        text_frame = Frame(
            1*inch, 
            2*inch, 
            width - 2*inch, 
            4*inch, 
            showBoundary=0
        )
        text_frame.addFromList([paragraph], p)
        
        # Footer (Date and Signature)
        p.setFont("Helvetica-Bold", 12)
        
        # Date
        date_str = self.object.issue_date.strftime("%d %B, %Y")
        p.drawString(1.5*inch, 2*inch, f"Date: {date_str}")
        
        # Signature Line
        p.line(width - 3.5*inch, 2.2*inch, width - 1.5*inch, 2.2*inch)
        p.drawString(width - 3*inch, 1.8*inch, "Principal's Signature")
        
        # Reference Number
        p.setFont("Helvetica", 8)
        p.drawString(0.5*inch, 0.5*inch, f"Ref: {self.object.certificate_number}")

        # Close the PDF object cleanly, and we're done.
        p.showPage()
        p.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        filename = f"Certificate_{self.object.certificate_number}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

class BulkCertificateCreateView(BaseView, FormView):
    """Bulk issue certificates for a class"""
    form_class = BulkCertificateForm
    template_name = 'certificates/bulk_certificate_form.html'
    permission_required = 'certificates.add_certificate'
    roles_required = ['admin', 'principal', 'registrar']
    success_url = reverse_lazy('certificates:certificate_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['tenant'] = self.tenant
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        class_group = form.cleaned_data['class_group']
        section = form.cleaned_data['section']
        certificate_type = form.cleaned_data['certificate_type']
        issue_date = form.cleaned_data['issue_date']
        content = form.cleaned_data['content']
        
        # Filter students
        students = Student.objects.filter(current_class=class_group, tenant=self.tenant, status='ACTIVE')
        if section:
            students = students.filter(section=section)
            
        created_count = 0
        for student in students:
            # Check if active certificate of same type already exists
            # Optional: Allow duplicates or assume new issue?
            # Let's check for duplicates issued today to prevent accidental double-clicks
            if not Certificate.objects.filter(
                student=student, 
                certificate_type=certificate_type, 
                issue_date=issue_date,
                tenant=self.tenant
            ).exists():
                Certificate.objects.create(
                    student=student,
                    certificate_type=certificate_type,
                    issue_date=issue_date,
                    content=content,
                    status='DRAFT', # Bulk issues started as Draft for review
                    tenant=self.tenant
                )
                created_count += 1
                
        if created_count > 0:
            messages.success(self.request, f"Successfully generated {created_count} certificates.")
        else:
            messages.warning(self.request, "No new certificates were generated. Check if students exist or certificates already issued.")
            
        return redirect(self.success_url)
