from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtracts the arg from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def split(value, arg=None):
    """Splits the string by the given argument (default is space)."""
    if arg is None:
        return value.split()
    return value.split(arg)
