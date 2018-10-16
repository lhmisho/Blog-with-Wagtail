from django.conf import settings # import the settings file

def django_settings(request):
    return {'django_settings': settings}