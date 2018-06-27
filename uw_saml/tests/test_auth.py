from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from uw_saml.auth import DjangoSAML, OneLogin_Saml2_Auth, Mock_Saml2_Auth
from uw_saml.tests import MOCK_SAML_ATTRIBUTES, MOCK_SESSION_ATTRIBUTES
import mock


class MockAuthTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().post(
            reverse('saml_sso'), HTTP_HOST='example.uw.edu')
        self.request.user = None
        SessionMiddleware().process_request(self.request)
        self.request.session.save()

    def test_implementation(self):
        with self.settings(MOCK_SAML_ATTRIBUTES=MOCK_SAML_ATTRIBUTES):
            auth = DjangoSAML(self.request)
            self.assertIsInstance(auth._implementation, Mock_Saml2_Auth)
            self.assertEquals(auth.get_nameid(), 'mock-nameid')
            self.assertEquals(auth.get_session_index(), 'mock-session-index')

    def test_get_attributes(self):
        with self.settings(MOCK_SAML_ATTRIBUTES=MOCK_SAML_ATTRIBUTES):
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
        with self.settings(MOCK_SAML_ATTRIBUTES=MOCK_SAML_ATTRIBUTES):
            auth = DjangoSAML(self.request)
            url = auth.login(return_to='/test')
            self.assertEquals(url, '/test')
            self.assertEquals(self.request.user.is_authenticated, True)
            self.assertEquals(self.request.user.username, 'javerage')

            # Missing return_to arg
            auth = DjangoSAML(self.request)
            self.assertEquals(auth.login(), '')

    def test_logout(self):
        with self.settings(MOCK_SAML_ATTRIBUTES=MOCK_SAML_ATTRIBUTES):
            auth = DjangoSAML(self.request)
            url = auth.logout(return_to='/test')
            self.assertEquals(url, '/test')
            self.assertEquals(self.request.user.is_authenticated, False)
            self.assertEquals(self.request.user.username, '')

            # Missing return_to arg
            auth = DjangoSAML(self.request)
            self.assertEquals(auth.logout(), '')

    def test_nonexistent_method(self):
        with self.settings(MOCK_SAML_ATTRIBUTES=MOCK_SAML_ATTRIBUTES):
            auth = DjangoSAML(self.request)
            self.assertRaises(AttributeError, auth.fake_method)


class LiveAuthTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().post(
            reverse('saml_sso'), data={'SAMLResponse': ''},
            HTTP_HOST='idp.uw.edu')
        SessionMiddleware().process_request(self.request)
        self.request.session.save()

    def test_implementation(self):
        auth = DjangoSAML(self.request)
        self.assertIsInstance(auth._implementation, OneLogin_Saml2_Auth)

    @mock.patch.object(OneLogin_Saml2_Auth, 'get_attributes')
    def test_get_attributes(self, mock_attributes):
        mock_attributes.return_value = MOCK_SAML_ATTRIBUTES

        auth = DjangoSAML(self.request)
        self.assertEquals(auth.get_attributes(), {
            'affiliations': ['student'],
            'eppn': ['javerage@washington.edu'], 'uwnetid': ['javerage'],
            'scopedAffiliations': ['student@washington.edu'],
            'isMemberOf': ['u_test_group', 'u_test2_group']})
