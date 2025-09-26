from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Custom filter to allow dictionary/object access with a dynamic key 
    in Django templates. Useful for dynamic table rendering.
    Usage: {{ row|get_item:column_header }}
    """
    try:
        return dictionary.get(key)
    except AttributeError:
        # Handle cases where 'dictionary' is not a dict-like object
        return None