from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Replaces all instances of the first argument in the value
    with the second argument.
    
    Usage: {{ value|replace:"_," }}
    """
    if len(arg.split(',')) != 2:
        return value
    
    old, new = arg.split(',')
    return value.replace(old, new)