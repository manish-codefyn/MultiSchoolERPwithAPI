import io
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
from apps.students.models import Student
from apps.exams.models import ExamResult, SubjectResult, MarkSheet
from apps.core.utils.tenant import get_current_tenant

class MarksheetGenerator:
    """
    A class to generate PDF marksheets using HTML templates.
    Follows the pattern of StudentIDCardGenerator but adapted for complex documents (PDFs).
    """
    def __init__(self, exam_result, request=None):
        self.result = exam_result
        self.student = exam_result.student
        self.exam = exam_result.exam
        self.request = request
        self.tenant = exam_result.tenant

    def _get_context(self):
        """Prepare context data for the template."""
        # Ensure MarkSheet exists
        mark_sheet, created = MarkSheet.objects.get_or_create(
            exam_result=self.result,
            defaults={
                'tenant': self.tenant,
                'issued_by': self.request.user if self.request and self.request.user.is_authenticated else None,
                'is_issued': True
            }
        )

        # Get parent details
        guardians = self.student.guardians.all()
        mother_name = "-"
        father_name = "-"
        
        for guardian in guardians:
            if guardian.relation == 'MOTHER':
                mother_name = guardian.full_name
            elif guardian.relation == 'FATHER':
                father_name = guardian.full_name
                
        if father_name == "-" and guardians.exists():
            father_name = guardians.first().full_name

        # Prepare context
        # Explicitly fetch configuration to ensure fresh data
        from apps.tenants.models import TenantConfiguration, TenantAddress
        try:
            config = TenantConfiguration.objects.get(tenant=self.tenant)
        except TenantConfiguration.DoesNotExist:
            config = None
            
        # Explicitly fetch address
        try:
            address = TenantAddress.objects.get(tenant=self.tenant)
        except TenantAddress.DoesNotExist:
            address = None

        # Resolve logo path for PDF
        logo_path = None
        if config and config.logo:
            try:
                logo_path = config.logo.path
            except NotImplementedError:
                # Fallback for storage backends that don't support path (like S3)
                # But for local dev (Windows user), path should work.
                pass

        return {
            'result': self.result,
            'mark_sheet': mark_sheet,
            'subject_results': SubjectResult.objects.filter(exam_result=self.result).select_related('exam_subject__subject', 'grade'),
            'tenant': self.tenant,
            'tenant_config': config,
            'tenant_address': address, # Added address object
            'logo_path': logo_path,
            'request': self.request,
            'mother_name': mother_name,
            'father_name': father_name,
            # Pass additional data if needed (e.g., colors from settings like icard)
        }

    def _generate_qr_code(self, mark_sheet):
        """Generate QR code base64 string for the marksheet."""
        import qrcode
        from io import BytesIO
        import base64
        
        # Data for QR code (Validation URL or Code)
        # Using verification URL if domain is available, else just the code info
        if self.tenant.domains.exists():
            domain = self.tenant.domains.first().domain
            qr_data = f"https://{domain}/verify-result/{mark_sheet.verification_code}/"
        else:
            qr_data = f"VERIFY:{mark_sheet.verification_code}|ROLL:{self.student.roll_number}"
            
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

    def generate_pdf(self):
        """Generates the PDF bytes."""
        context = self._get_context()
        
        # Add QR code to context
        mark_sheet = context['mark_sheet']
        context['qr_code_base64'] = self._generate_qr_code(mark_sheet)
        
        html = render_to_string('exams/pdf/mark_sheet_pdf.html', context)
        
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
        
        if pisa_status.err:
            return None
            
        pdf_buffer.seek(0)
        return pdf_buffer

    def get_response(self):
        """Return a Django HttpResponse with the PDF."""
        pdf_buffer = self.generate_pdf()
        
        if not pdf_buffer:
            return HttpResponse('Error generating PDF', status=500)
            
        filename = f"Mark_Sheet_{self.student.roll_number}_{self.exam.name}.pdf"
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
