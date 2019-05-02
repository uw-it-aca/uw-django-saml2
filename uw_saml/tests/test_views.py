from django.conf import settings
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from uw_saml.views import LoginView, LogoutView, SSOView
from uw_saml.auth import OneLogin_Saml2_Auth
from uw_saml.tests import MOCK_SAML_ATTRIBUTES
import mock

CACHE_CONTROL = 'max-age=0, no-cache, no-store, must-revalidate'


class LoginViewTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().get(
            reverse('saml_login'), HTTP_HOST='example.uw.edu')
        SessionMiddleware().process_request(self.request)
        self.request.session.save()

    def test_login(self):
        view_instance = LoginView.as_view()
        response = view_instance(self.request)
        self.assertEquals(response.status_code, 302)
        self.assertIn(settings.UW_SAML['idp']['singleSignOnService']['url'],
                      response.url)
        self.assertEquals(response['Cache-Control'], CACHE_CONTROL)


class LogoutViewTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().get(
            reverse('saml_logout'), HTTP_HOST='example.uw.edu')
        SessionMiddleware().process_request(self.request)
        self.request.session['samlNameId'] = ''
        self.request.session['samlSessionIndex'] = ''
        self.request.session.save()

    def test_logout(self):
        view_instance = LogoutView.as_view()
        response = view_instance(self.request)
        self.assertEquals(response.status_code, 302)
        self.assertIn(settings.UW_SAML['idp']['singleLogoutService']['url'],
                      response.url)
        self.assertEquals(response['Cache-Control'], CACHE_CONTROL)


class SSOViewTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().post(
            reverse('saml_sso'),
            data={'RelayState': '/private'},
            HTTP_HOST='example.uw.edu')
        SessionMiddleware().process_request(self.request)
        self.request.session.save()

    @mock.patch.object(OneLogin_Saml2_Auth, 'get_attributes')
    @mock.patch.object(OneLogin_Saml2_Auth, 'process_response')
    def test_sso(self, mock_process_response, mock_get_attributes):
        mock_get_attributes.return_value = MOCK_SAML_ATTRIBUTES

        view_instance = SSOView.as_view()
        response = view_instance(self.request)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, 'http://example.uw.edu/private')


class SSOViewErrorTest(TestCase):
    def test_sso_error(self):
        # Missing POST data
        request = RequestFactory().post(
            reverse('saml_sso'), HTTP_HOST='example.uw.edu')
        SessionMiddleware().process_request(request)
        request.session.save()

        view_instance = SSOView.as_view()
        response = view_instance(request)
        self.assertContains(response, 'SSO Error:', status_code=400)

        # Invalid SAMLResponse
        request = RequestFactory().post(
            reverse('saml_sso'), data={'SAMLResponse': ''},
            HTTP_HOST='idp.uw.edu')
        SessionMiddleware().process_request(request)
        request.session.save()

        view_instance = SSOView.as_view()
        response = view_instance(request)
        self.assertContains(response, 'SSO Error:', status_code=400)

        # Invalid HTTP method
        request = RequestFactory().get(
            reverse('saml_sso'), HTTP_HOST='idp.uw.edu')
        SessionMiddleware().process_request(request)
        request.session.save()

        view_instance = SSOView.as_view()
        response = view_instance(request)
        self.assertEquals(response.status_code, 405)
