from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from onelogin.saml2.auth import OneLogin_Saml2_Auth


class DjangoSAML(OneLogin_Saml2_Auth):
    def __init__(self, request):
        if not hasattr(settings, 'UW_SAML'):
            raise ImproperlyConfigured('Missing "UW_SAML" key in settings.py')

        request_data = {
            'https': 'on' if request.is_secure() else 'off',
            'http_host': request.META['HTTP_HOST'],
            'script_name': request.META['PATH_INFO'],
            'server_port': request.META['SERVER_PORT'],
            'get_data': request.GET.copy(),
            'post_data': request.POST.copy(),
            'query_string': request.META['QUERY_STRING']
        }
        super(OneLogin_Saml2_Auth, self).__init__(
            request_data, old_settings=getattr(settings, 'UW_SAML'))
