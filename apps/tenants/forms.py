from django import forms
from .models import TenantAddress, TenantConfiguration, Tenant

class TenantAddressForm(forms.ModelForm):
    """
    Form for managing tenant address
    """
    class Meta:
        model = TenantAddress
        fields = [
            'address_line_1', 'address_line_2',
            'city', 'state', 'postal_code', 'country'
        ]
        widgets = {
            'address_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartment, Suite, Unit, etc.'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TenantConfigurationForm(forms.ModelForm):
    """
    Form for managing tenant configuration
    """
    class Meta:
        model = TenantConfiguration
        fields = '__all__'
        exclude = ['tenant', 'created_at', 'updated_at', 'id']
        widgets = {
            'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
            'timezone': forms.TextInput(attrs={'class': 'form-control'}),
            'language': forms.TextInput(attrs={'class': 'form-control'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'date_format': forms.TextInput(attrs={'class': 'form-control'}),
            # Add other widgets as needed
        }
