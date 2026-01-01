from django.contrib import admin
from apps.certificates.models import Certificate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'student', 'certificate_type', 'issue_date', 'status', 'tenant')
    list_filter = ('certificate_type', 'status', 'issue_date', 'tenant')
    search_fields = ('certificate_number', 'student__first_name', 'student__last_name', 'student__admission_number')
    readonly_fields = ('certificate_number', 'created_at', 'updated_at')
