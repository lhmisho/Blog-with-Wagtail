import re

from django.conf import settings
from django.utils import translation
from django.utils.encoding import force_text
from django.utils.html import strip_spaces_between_tags

from base import utils
from base.models import ApplicationSettings

RE_MULTISPACE = re.compile(r"\s{2,}")
RE_NEWLINE = re.compile(r"\n")

def MinifyHTMLMiddleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        response = get_response(request)

        if 'text/html' in response.get('Content-Type', []) and settings.COMPRESS_HTML:
            response.content = strip_spaces_between_tags(response.content)
            # response.content = RE_MULTISPACE.sub(" ", force_text(response.content))
            # response.content = RE_NEWLINE.sub("", force_text(response.content))
            response['Content-Length'] = len(response.content)
        return response

    return middleware



def ThemeMiddleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        utils.CURRENT_THEME = ApplicationSettings.for_site(request.site).theme
        response = get_response(request)
        return response

    return middleware

