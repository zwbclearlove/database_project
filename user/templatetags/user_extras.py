from django import template
from ..models import *

register = template.Library()

@register.inclusion_tag('user/inclusions/_footer.html',takes_context=True)
def show_footer(context):

    return {

    }

@register.inclusion_tag('user/inclusions/_nav_part.html',takes_context=True)
def show_nav_part(context):
    request = context['request']
    return {
        'request': request,
    }