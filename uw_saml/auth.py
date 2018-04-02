from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ImproperlyConfigured
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from uw_saml.utils import get_user


class DjangoSAML(object):
    """
    This class acts as a wrapper around an instance of either a
    OneLogin_Saml2_Auth or Mock_Saml2_Auth class.
    """
    def __init__(self, request):
        self._is_mock = False
        self._request = request

        if hasattr(settings, 'MOCK_SAML_ATTRIBUTES'):
            self._is_mock = True
            self._implementation = Mock_Saml2_Auth()

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

            self._implementation = OneLogin_Saml2_Auth(
                request_data, old_settings=getattr(settings, 'UW_SAML'))

        else:
            raise ImproperlyConfigured('Missing "UW_SAML" key in settings.py')

    def __getattr__(self, name, *args, **kwargs):
        """
        Pass method calls through to the implementation instance.
        """
        def handler(*args, **kwargs):
            return getattr(self._implementation, name)(*args, **kwargs)
        return handler

    def login(self, return_to=None):
        if self._is_mock:
            self.persist_login()

        return self._implementation.login(return_to=return_to)

    def persist_login(self):
        self._request.session['samlUserdata'] = self.get_attributes()
        self._request.session['samlNameId'] = self.get_nameid()
        self._request.session['samlSessionIndex'] = self.get_session_index()

        # Django login
        user = authenticate(self._request, remote_user=get_user(self._request))
        if user is not None:
            login(self._request, user)

    def logout(self, return_to=None):
        name_id = self._request.session.get('samlNameId')
        session_index = self._request.session.get('samlSessionIndex')

        logout(self._request)  # Django logout

        return self._implementation.logout(
            return_to=return_to, name_id=name_id, session_index=session_index)

    def get_attributes(self):
        """
        Return a dict of SAML attributes, mapping the default names to
        friendlier names for our apps.
        """
        attribute_map = {
            'urn:oid:0.9.2342.19200300.100.1.1': 'uwnetid',
            'urn:oid:1.3.6.1.4.1.5923.1.1.1.6': 'eppn',
            'urn:oid:1.2.840.113994.200.24': 'uwregid',
            'urn:oid:0.9.2342.19200300.100.1.3': 'email',
            'urn:oid:2.5.4.42': 'givenName',
            'urn:oid:2.5.4.4': 'surname',
            'urn:oid:1.2.840.113994.200.21': 'studentid',
            'urn:oid:1.3.6.1.4.1.5923.1.1.1.1': 'affiliations',
            'urn:oid:1.3.6.1.4.1.5923.1.1.1.9': 'scopedAffiliations',
            'urn:oid:1.3.6.1.4.1.5923.1.5.1.1': 'isMemberOf',
        }

        attributes = {attribute_map.get(key, key): value for key, value in (
            self._implementation.get_attributes().items())}

        if 'isMemberOf' in attributes:
            group_urn = 'urn:mace:washington.edu:groups:'
            attributes['isMemberOf'] = [el.replace(group_urn, '') for el in (
                attributes['isMemberOf'])]

        return attributes


class Mock_Saml2_Auth(object):
    def login(self, return_to='/', **kwargs):
        return return_to

    def logout(self, return_to='/', **kwargs):
        return return_to

    def get_attributes(self):
        return getattr(settings, 'MOCK_SAML_ATTRIBUTES')

    def get_nameid(self):
        return 'mock-nameid'

    def get_session_index(self):
        return 'mock-session-index'
