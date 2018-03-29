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

        super(DjangoSAML, self).__init__(
            request_data, old_settings=getattr(settings, 'UW_SAML'))

    def get_attributes(self):
        """
        Return a dict of SAML attributes, mapping the default names to
        friendlier names for our apps.
        """
        attribute_map = {
            'urn:oid:0.9.2342.19200300.100.1.1': 'uwnetid',
            'urn:oid:1.3.6.1.4.1.5923.1.1.1.1': 'affiliations',
            'urn:oid:1.3.6.1.4.1.5923.1.1.1.6': 'eppn',
            'urn:oid:1.3.6.1.4.1.5923.1.1.1.9': 'scopedAffiliations'
        }

        return {
            attribute_map.get(key, key): value for key, value in super(
                DjangoSAML, self).get_attributes().items()}
