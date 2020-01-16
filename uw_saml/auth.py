from django.conf import settings
from django.contrib.auth import (
    authenticate, login, logout, REDIRECT_FIELD_NAME)
from django.contrib.auth.models import User
from django.core.exceptions import (
    ImproperlyConfigured, ObjectDoesNotExist, PermissionDenied)
from django.urls import reverse_lazy
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from uw_saml.utils import get_user


class DjangoSAML(object):
    """
    This class acts as a wrapper around an instance of either a
    OneLogin_Saml2_Auth or a Mock_Saml2_Auth class.
    """
    FORWARDED_HOST = 'HTTP_X_FORWARDED_HOST'
    FORWARDED_PORT = 'HTTP_X_FORWARDED_PORT'
    FORWARDED_PROTO = 'HTTP_X_FORWARDED_PROTO'

    ATTRIBUTE_MAP = {
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
    GROUP_NS = 'urn:mace:washington.edu:groups:'

    def __init__(self, request):
        self._request = request

        if hasattr(settings, 'MOCK_SAML_ATTRIBUTES'):
            self._implementation = Mock_Saml2_Auth()
            self.process_response()

        elif hasattr(settings, 'DJANGO_LOGIN_MOCK_SAML'):
            self._implementation = Django_Login_Mock_Saml2_Auth(request)

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

            if self.FORWARDED_HOST in request.META:
                request_data['http_host'] = request.META[self.FORWARDED_HOST]

            if self.FORWARDED_PORT in request.META:
                request_data['server_port'] = request.META[self.FORWARDED_PORT]

            if self.FORWARDED_PROTO in request.META:
                request_data['https'] = 'on' if (
                    request.META[self.FORWARDED_PROTO] == 'https') else 'off'

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

    def login(self, **kwargs):
        """
        Overrides the implementation method to add force_authn option.
        """
        kwargs['force_authn'] = getattr(settings, 'SAML_FORCE_AUTHN', False)
        return self._implementation.login(**kwargs)

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
        attributes = {self.ATTRIBUTE_MAP.get(key, key): val for key, val in (
            self._implementation.get_attributes().items())}

        if 'isMemberOf' in attributes:
            attributes['isMemberOf'] = [e.replace(self.GROUP_NS, '') for e in (
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


class Django_Login_Mock_Saml2_Auth(object):
    def __init__(self, request):
        self.dl_saml_data = getattr(
            settings, 'DJANGO_LOGIN_MOCK_SAML'
        )
        for user in self.dl_saml_data['SAML_USERS']:
            try:
                User.objects.get(username=user["username"])
            except ObjectDoesNotExist:
                User.objects.create_user(
                    user["username"],
                    email=user["email"],
                    password=user["password"]
                ).save()
        self.request = request

    def login(self, **kwargs):
        return "{}?{}={}".format(
            reverse_lazy('login_django'), REDIRECT_FIELD_NAME,
            kwargs.get('return_to', '')
        )

    def logout(self, **kwargs):
        return kwargs.get('return_to', '')

    def process_response(self):
        if self.request.user.is_authenticated:
            self.username = self.request.user.username
        else:
            raise PermissionDenied(
                'The request must be authenticated before it can be processed'
            )
        return

    def get_attributes(self):
        for i, user in enumerate(self.dl_saml_data['SAML_USERS']):
            if (user["username"] == self.username):
                return user['MOCK_ATTRIBUTES']
        raise ImproperlyConfigured('This user does not exist in SAML_USERS')

    def get_nameid(self):
        if 'NAME_ID' in self.dl_saml_data:
            return self.dl_saml_data['NAME_ID']
        return 'mock-nameid'

    def get_session_index(self):
        if 'SESSION_INDEX' in self.dl_saml_data:
            return self.dl_saml_data['SESSION_INDEX']
        return 'mock-session'

    def get_errors(self):
        return []

    def redirect_to(self, url):
        return url
