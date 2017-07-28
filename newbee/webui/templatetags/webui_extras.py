from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    # REF: http://stackoverflow.com/questions/8000022/django-template-how-to-lookup-a-dictionary-value-with-a-variable
    # Usage: handling errors in templates

    return dictionary.get(key)
