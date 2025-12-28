
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()  # This is IMPORTANT


class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form with email as username"""
    username = forms.EmailField(
        label=_("Email Address"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email',
        })
    )
    
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )
    
    def clean(self):
        """Add custom validation"""
        cleaned_data = super().clean()
        
        # Check if user is active
        username = cleaned_data.get('username')
        if username:
            try:
                user = User.objects.get(email=username)
                if not user.is_active:
                    raise ValidationError(
                        _("This account is inactive. Please contact administrator."),
                        code='inactive_account',
                    )
                
                if hasattr(user, 'is_account_locked') and user.is_account_locked:
                    raise ValidationError(
                        _("Your account is locked due to too many failed login attempts. "
                          "Please contact administrator or try again later."),
                        code='locked_account',
                    )
                
            except User.DoesNotExist:
                pass  # Let parent form handle this
        
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = User 
        exclude = ['timezone', 'language']
        fields = [
            'first_name', 'last_name', 'phone_number',
            'date_of_birth',
            'avatar', 
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890',
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'timezone': forms.Select(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_phone_number(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Basic validation - you can add more sophisticated validation
            import re
            if not re.match(r'^\+?1?\d{9,15}$', phone):
                raise ValidationError(
                    _("Enter a valid phone number in the format: '+1234567890'")
                )
        return phone

    def clean_avatar(self):
        """Validate avatar"""
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Check file size (e.g., 2MB limit)
            if hasattr(avatar, 'size') and avatar.size > 2 * 1024 * 1024:
                raise ValidationError(_("Image file too large ( > 2mb )"))
            
        return avatar


class SignupForm(forms.ModelForm):
    """Form for user registration"""
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'new-password',
        })
    )
    confirm_password = forms.CharField(
        label=_("Confirm Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password',
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'name@example.com',
                'autocomplete': 'email',
            }),
        }
        
    def clean_email(self):
        """Check if email already exists"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError(
                _("A user with this email already exists."),
                code='duplicate_email'
            )
        return email
        
    def clean(self):
        """Validate passwords match"""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', _("Passwords do not match"))
            

    def save(self, commit=True):
        """Save user with password"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class MFASetupForm(forms.Form):
    """Dummy MFA Setup Form"""
    verification_code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center', 
            'placeholder': '000000',
            'pattern': '[0-9]*', 
            'inputmode': 'numeric',
            'maxlength': '6'
        })
    )

class MFAVerifyForm(forms.Form):
    """Dummy MFA Verify Form"""
    verification_code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center', 
            'placeholder': '000000',
            'pattern': '[0-9]*', 
            'inputmode': 'numeric',
            'maxlength': '6'
        })
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with security checks"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'new-password'
            })
    
    def clean_new_password2(self):
        """Validate password strength"""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Passwords do not match."))
        
        if password1 and len(password1) < 8:
            raise ValidationError(_("Password must be at least 8 characters long."))
        
        return password2
