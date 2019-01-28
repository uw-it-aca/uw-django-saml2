import logging
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ImproperlyConfigured
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from uw_saml.utils import get_user
import sys

logger = logging.getLogger(__name__)


class DjangoSAML(object):
    """
    This class acts as a wrapper around an instance of either a
    OneLogin_Saml2_Auth or a Mock_Saml2_Auth class.
    """
    attribute_map = {
        'urn:oid:0.9.2342.19200300.100.1.1': 'uwnetid',
        'urn:oid:1.3.6.1.4.1.5923.1.1.1.6': 'eppn',
        'urn:oid:1.2.840.113994.200.24': 'uwregid',
        'urn:oid:0.9.2342.19200300.100.1.3': 'email',
        'urn:oid:2.16.840.1.113730.3.1.241': 'displayName',
        'urn:oid:2.5.4.42': 'givenName',
        'urn:oid:2.5.4.4': 'surname',
        'urn:oid:1.2.840.113994.200.21': 'studentid',
        'urn:oid:2.16.840.1.113730.3.1.3': 'employeeNumber',
        'urn:oid:2.5.4.11': 'homeDepartment',
        'urn:oid:1.3.6.1.4.1.5923.1.1.1.1': 'affiliations',
        'urn:oid:1.3.6.1.4.1.5923.1.1.1.9': 'scopedAffiliations',
        'urn:oid:1.3.6.1.4.1.5923.1.5.1.1': 'isMemberOf',
    }
    group_ns = 'urn:mace:washington.edu:groups:'

    def __init__(self, request):
        self._request = request

        if hasattr(settings, 'MOCK_SAML_ATTRIBUTES'):
            self._implementation = Mock_Saml2_Auth()
            self.process_response()

        elif hasattr(settings, 'UW_SAML'):
            request_data = {
                'https': 'on' if request.is_secure() else 'off',
                'http_host': request.META['HTTP_HOST'],
                'script_name': request.META['PATH_INFO'],
                'server_port': request.META['SERVER_PORT'],
                'get_data': request.GET.copy(),
                'post_data': request.POST.copy(),
                'query_string': request.META['QUERY_STRING']
            }

            logger.info("Request data Preprocessing %s", request_data)
            sys.stdout.write(str(request_data))
            sys.stdout.write(str(request.META))

            if hasattr(request.META, "HTTP_X_FORWARDED_HOST"):
                request_data["http_host"] = request.META["X-Forwarded-Host"]

            if hasattr(request.META, "HTTP_X_FORWARDED_PORT"):
                request_data["server_port"] = request.META["X-Forwarded-Port"]

            if getattr(request.META, "HTTP_X_FORWARDED_PROTO", "http") == "https":
                request_data['https'] = 'on'

            logger.info("Request data Postprocessing %s", request_data)
            sys.stdout.write(str(request_data))

            self._implementation = OneLogin_Saml2_Auth(
                request_data, old_settings=getattr(settings, 'UW_SAML'))

        else:
            raise ImproperlyConfigured('Missing "UW_SAML" dict in settings.py')

    def __getattr__(self, name, *args, **kwargs):
        """
        Pass unshimmed method calls through to the implementation instance.
        """
        def handler(*args, **kwargs):
            return getattr(self._implementation, name)(*args, **kwargs)
        return handler

    def logout(self, **kwargs):
        """
        Overrides the implementation method to add the Django logout.
        """
        kwargs['name_id'] = self._request.session.get('samlNameId')
        kwargs['session_index'] = self._request.session.get('samlSessionIndex')

        # Django logout
        logout(self._request)

        return self._implementation.logout(**kwargs)

    def process_response(self):
        """
        Overrides the implementation method to store the SAML attributes and
        add the Django login.
        """
        self._implementation.process_response()

        self._request.session['samlUserdata'] = self.get_attributes()
        self._request.session['samlNameId'] = self.get_nameid()
        self._request.session['samlSessionIndex'] = self.get_session_index()

        # Django login
        user = authenticate(self._request, remote_user=get_user(self._request))
        login(self._request, user)

    def get_attributes(self):
        """
        Overrides the implementation method to return a dictionary of SAML
        attributes, mapping the default names to friendlier names.
        """
        attributes = {self.attribute_map.get(key, key): val for key, val in (
            self._implementation.get_attributes().items())}

        if 'isMemberOf' in attributes:
            attributes['isMemberOf'] = [e.replace(self.group_ns, '') for e in (
                attributes['isMemberOf'])]

        return attributes


class Mock_Saml2_Auth(object):
    def login(self, **kwargs):
        return kwargs.get('return_to', '')

    def logout(self, **kwargs):
        return kwargs.get('return_to', '')

    def process_response(self):
        return

    def get_attributes(self):
        return getattr(settings, 'MOCK_SAML_ATTRIBUTES')

    def get_nameid(self):
        return 'mock-nameid'

    def get_session_index(self):
        return 'mock-session-index'
