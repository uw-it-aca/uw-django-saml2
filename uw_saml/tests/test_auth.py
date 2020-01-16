from django.conf import settings
from django.urls import reverse, reverse_lazy, clear_url_caches
from django.core.exceptions import ImproperlyConfigured, PermissionDenied,\
    ImproperlyConfigured
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory, override_settings
from uw_saml.auth import DjangoSAML, OneLogin_Saml2_Auth, Mock_Saml2_Auth,\
    Django_Login_Mock_Saml2_Auth
from uw_saml.tests import MOCK_SAML_ATTRIBUTES, MOCK_SESSION_ATTRIBUTES,\
    UW_SAML_PERMISSIONS, DJANGO_LOGIN_MOCK_SAML
import mock
import sys
from importlib import reload


@override_settings(MOCK_SAML_ATTRIBUTES=MOCK_SAML_ATTRIBUTES)
class MockAuthTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().post(
            reverse('saml_sso'), HTTP_HOST='example.uw.edu')
        self.request.user = None
        SessionMiddleware().process_request(self.request)
        self.request.session.save()

    def test_implementation(self):
        auth = DjangoSAML(self.request)
        self.assertIsInstance(auth._implementation, Mock_Saml2_Auth)
        self.assertEquals(auth.get_nameid(), 'mock-nameid')
        self.assertEquals(auth.get_session_index(), 'mock-session-index')

    def test_get_attributes(self):
        auth = DjangoSAML(self.request)
        self.assertEquals(auth.get_attributes(), {
            'affiliations': ['student'],
            'eppn': ['javerage@washington.edu'], 'uwnetid': ['javerage'],
            'scopedAffiliations': ['student@washington.edu'],
            'isMemberOf': ['u_test_group', 'u_test2_group']})

        with self.settings(MOCK_SAML_ATTRIBUTES=MOCK_SESSION_ATTRIBUTES):
            auth = DjangoSAML(self.request)
            self.assertEquals(auth.get_attributes(), {
                'affiliations': ['student'],
                'eppn': ['javerage@washington.edu'], 'uwnetid': ['javerage'],
                'scopedAffiliations': ['student@washington.edu'],
                'isMemberOf': ['u_test_group', 'u_test2_group']})

    def test_login(self):
        auth = DjangoSAML(self.request)
        url = auth.login(return_to='/test')
        self.assertEquals(url, '/test')
        self.assertEquals(self.request.user.is_authenticated, True)
        self.assertEquals(self.request.user.username, 'javerage')

        # Missing return_to arg
        auth = DjangoSAML(self.request)
        self.assertEquals(auth.login(), '')

    def test_logout(self):
        auth = DjangoSAML(self.request)
        url = auth.logout(return_to='/test')
        self.assertEquals(url, '/test')
        self.assertEquals(self.request.user.is_authenticated, False)
        self.assertEquals(self.request.user.username, '')

        # Missing return_to arg
        auth = DjangoSAML(self.request)
        self.assertEquals(auth.logout(), '')

    def test_nonexistent_method(self):
        auth = DjangoSAML(self.request)
        self.assertRaises(AttributeError, auth.fake_method)


@override_settings(
    UW_SAML_PERMISSIONS=UW_SAML_PERMISSIONS,
    DJANGO_LOGIN_MOCK_SAML=DJANGO_LOGIN_MOCK_SAML,
    AUTHENTICATION_BACKENDS=('django.contrib.auth.backends.ModelBackend',)
)
class DjangoLoginAuthTest(TestCase):
    def setUp(self):
        clear_url_caches()
        reload(sys.modules['uw_saml.urls'])
        reload(sys.modules[settings.ROOT_URLCONF])
        self.request = RequestFactory().post(
            reverse('saml_sso'), data={'SAMLResponse': ''},
            HTTP_HOST='idp.uw.edu')
        SessionMiddleware().process_request(self.request)
        self.request.session.save()

    def test_implementation(self):
        auth = DjangoSAML(self.request)
        self.assertIsInstance(
            auth._implementation,
            Django_Login_Mock_Saml2_Auth
        )

    def test_login(self):
        auth = DjangoSAML(self.request)
        self.assertEqual(
            auth.login(return_to='return_to_url'),
            "{}?next={}".format(
                reverse_lazy('login_django'),
                'return_to_url'
            )
        )

    def test_logout(self):
        auth = DjangoSAML(self.request)
        self.assertEqual(
            auth.logout(return_to='return_to_url'),
            "{}".format('return_to_url')
        )

    def test_bad_process_response(self):
        self.request.user = AnonymousUser()
        auth = DjangoSAML(self.request)
        with self.assertRaises(PermissionDenied):
            auth.process_response()

    def test_get_attributes(self):
        auth = DjangoSAML(self.request)
        auth._implementation.username = 'test_username'
        self.assertEquals(
            auth.get_attributes(),
            settings.DJANGO_LOGIN_MOCK_SAML['SAML_USERS'][0]['MOCK_ATTRIBUTES']
        )

    def test_bad_get_attributes(self):
        auth = DjangoSAML(self.request)
        auth._implementation.username = 'test_not_username'
        with self.assertRaises(ImproperlyConfigured):
            auth.get_attributes()

    def test_get_nameid(self):
        auth = DjangoSAML(self.request)
        self.assertEquals(
            auth.get_nameid(),
            'test-mock-nameid'
        )
        del settings.DJANGO_LOGIN_MOCK_SAML['NAME_ID']
        self.assertEquals(
            auth.get_nameid(),
            'mock-nameid'
        )

    def test_get_session_index(self):
        auth = DjangoSAML(self.request)
        self.assertEquals(
            auth.get_session_index(),
            'test-mock-session'
        )
        del settings.DJANGO_LOGIN_MOCK_SAML['SESSION_INDEX']
        self.assertEquals(
            auth.get_session_index(),
            'mock-session'
        )


class LiveAuthTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().post(
            reverse('saml_sso'), data={'SAMLResponse': ''},
            HTTP_HOST='idp.uw.edu')
        SessionMiddleware().process_request(self.request)
        self.request.session.save()

    @override_settings()
    def test_missing_implementation(self):
        del settings.UW_SAML
        self.assertRaises(ImproperlyConfigured, DjangoSAML, self.request)

    def test_implementation(self):
        auth = DjangoSAML(self.request)
        self.assertIsInstance(auth._implementation, OneLogin_Saml2_Auth)

    @mock.patch.object(OneLogin_Saml2_Auth, 'login')
    def test_login(self, mock_login):
        auth = DjangoSAML(self.request)
        url = auth.login(return_to='/test')
        mock_login.assert_called_with(force_authn=False, return_to='/test')

        with self.settings(SAML_FORCE_AUTHN=True):
            auth = DjangoSAML(self.request)
            url = auth.login(return_to='/test')
            mock_login.assert_called_with(force_authn=True, return_to='/test')

    @mock.patch.object(OneLogin_Saml2_Auth, 'get_attributes')
    def test_get_attributes(self, mock_attributes):
        mock_attributes.return_value = MOCK_SAML_ATTRIBUTES

        auth = DjangoSAML(self.request)
        self.assertEquals(auth.get_attributes(), {
            'affiliations': ['student'],
            'eppn': ['javerage@washington.edu'], 'uwnetid': ['javerage'],
            'scopedAffiliations': ['student@washington.edu'],
            'isMemberOf': ['u_test_group', 'u_test2_group']})
