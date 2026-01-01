from django import forms
from apps.core.forms import TenantAwareModelForm, BaseForm
from apps.certificates.models import Certificate
from apps.academics.models import SchoolClass, Section
from django.utils.translation import gettext_lazy as _

class CertificateForm(TenantAwareModelForm):
    """Form for creating and updating certificates"""
    class Meta:
        model = Certificate
        fields = ['student', 'certificate_type', 'issue_date', 'content', 'status']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'content': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-select select2'}),
            'certificate_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class BulkCertificateForm(forms.Form):
    """Form for bulk generation"""
    class_group = forms.ModelChoiceField(
        queryset=SchoolClass.objects.all(),
        label=_("Class"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    section = forms.ModelChoiceField(
        queryset=Section.objects.all(),
        label=_("Section (Optional)"),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    certificate_type = forms.ChoiceField(
        choices=Certificate.CERTIFICATE_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    issue_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        required=False,
        help_text=_("Common content for all certificates")
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.tenant = kwargs.pop('tenant', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.tenant:
            self.fields['class_group'].queryset = SchoolClass.objects.filter(tenant=self.tenant)
            self.fields['section'].queryset = Section.objects.filter(tenant=self.tenant)
