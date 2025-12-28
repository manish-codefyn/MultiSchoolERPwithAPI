# In apps/core/utils/validators.py
import re
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


def validate_phone_number(value):
    """Validate phone number"""
    pattern = r"^\+?1?\d{9,15}$"
    if not re.match(pattern, value):
        raise ValidationError(
            _('Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.')
        )
    return value


def validate_aadhaar_number(value):
    """Validate Aadhaar number (12 digits)"""
    pattern = r'^\d{12}$'
    if not re.match(pattern, value):
        raise ValidationError(_('Aadhaar number must be 12 digits.'))
    return value


def validate_pan_number(value):
    """Validate PAN number"""
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    if not re.match(pattern, value):
        raise ValidationError(_('Invalid PAN format. Example: ABCDE1234F'))
    return value


def validate_ifsc_code(value):
    """Validate IFSC code"""
    pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
    if not re.match(pattern, value):
        raise ValidationError(_('Invalid IFSC code format.'))
    return value


def validate_date_not_future(value):
    """Validate date is not in the future"""
    from django.utils import timezone
    if value > timezone.now().date():
        raise ValidationError(_('Date cannot be in the future.'))
    return value


def validate_age_range(min_age=3, max_age=100):
    """Validate age is within range"""
    def validator(value):
        from django.utils import timezone
        today = timezone.now().date()
        age = today.year - value.year - (
            (today.month, today.day) < (value.month, value.day)
        )
        if age < min_age or age > max_age:
            raise ValidationError(
                _(f'Age must be between {min_age} and {max_age} years.')
            )
        return value
    return validator


def validate_email_domain(value):
    """Validate email domain is not from temporary email services"""
    invalid_domains = [
        'tempmail.com', 'yopmail.com', 'mailinator.com',
        'guerrillamail.com', 'trashmail.com', '10minutemail.com'
    ]
    domain = value.split('@')[-1].lower()
    if domain in invalid_domains:
        raise ValidationError(_('Temporary email addresses are not allowed.'))
    return value


def validate_file_size(max_size_mb):
    """Validate file size"""
    max_size = max_size_mb * 1024 * 1024
    
    def validator(value):
        if value.size > max_size:
            raise ValidationError(
                _(f'File size must be less than {max_size_mb}MB.')
            )
        return value
    return validator


def validate_file_extension(allowed_extensions):
    """Validate file extension"""
    def validator(value):
        ext = value.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise ValidationError(
                _(f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}')
            )
        return value
    return validator