from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from uw_saml import DjangoSAML, OneLogin_Saml2_Auth
from uw_saml.tests import MOCK_ATTRS
import mock


class AuthTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().post(
            reverse('saml_sso'), data={'SAMLResponse': ''},
            HTTP_HOST='idp.uw.edu')
        SessionMiddleware().process_request(self.request)
        self.request.session.save()

    @mock.patch.object(OneLogin_Saml2_Auth, 'get_attributes')
    def test_get_attributes(self, mock_attributes):
        mock_attributes.return_value = MOCK_ATTRS

        auth = DjangoSAML(self.request)
        self.assertEquals(auth.get_attributes(), {
            'affiliations': ['student'], 'eppn': ['javerage@washington.edu'],
            'uwnetid': ['javerage'],
            'scopedAffiliations': ['student@washington.edu']})

    @mock.patch.object(OneLogin_Saml2_Auth, 'get_attributes')
    def test_get_remote_user(self, mock_attributes):
        mock_attributes.return_value = MOCK_ATTRS

        auth = DjangoSAML(self.request)
        self.assertEquals(auth.get_remote_user(),
                          'javerage', "No setting, default is 'uwnetid'")

        with self.settings(SAML_USER_ATTRIBUTE='uwnetid'):
            auth = DjangoSAML(self.request)
            self.assertEquals(auth.get_remote_user(), 'javerage')

        with self.settings(SAML_USER_ATTRIBUTE='eppn'):
            auth = DjangoSAML(self.request)
            self.assertEquals(auth.get_remote_user(),
                              'javerage@washington.edu')
