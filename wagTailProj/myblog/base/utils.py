from django.conf import settings

CURRENT_THEME = 'default'

def template_tag_load_string():
    return "{% load "+ " ".join(settings.TEMPLATE_TAGS_FOR_TEXTAREAS) +" %}"
