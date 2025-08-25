from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Replaces all occurrences of a substring with another substring
    Usage: {{ value|replace:"old,new" }}
    """
    if ',' in arg:
        old, new = arg.split(',', 1)
        return value.replace(old, new)
    return value

@register.filter
def underscore_to_space(value):
    """Converts underscores to spaces"""
    return value.replace('_', ' ')