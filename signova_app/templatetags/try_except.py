from django import template
from django.template.base import Node, NodeList, TemplateSyntaxError

register = template.Library()

class TryExceptNode(Node):
    def __init__(self, try_nodes, except_nodes):
        self.try_nodes = try_nodes
        self.except_nodes = except_nodes

    def render(self, context):
        try:
            return self.try_nodes.render(context)
        except Exception:
            return self.except_nodes.render(context)

@register.tag
def try_except(parser, token):
    """
    The ``{% try %} ... {% except %} ... {% endtry %}`` tag.
    
    This tag catches exceptions in the enclosed code and renders
    the except block if an exception occurs.
    
    Usage::
    
        {% try %}
            ... code that might raise an exception ...
        {% except %}
            ... code to run if an exception is raised ...
        {% endtry %}
    """
    bits = token.split_contents()
    if len(bits) != 1:
        raise TemplateSyntaxError("'%s' takes no arguments" % bits[0])
    
    try_nodes = parser.parse(('except',))
    parser.delete_first_token()
    
    except_nodes = parser.parse(('endtry',))
    parser.delete_first_token()
    
    return TryExceptNode(try_nodes, except_nodes)