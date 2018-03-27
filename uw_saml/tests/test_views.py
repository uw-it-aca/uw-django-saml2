from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from uw_saml.views import LoginView, LogoutView, SSOView
import mock


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


class SSOViewTest(TestCase):
    def test_sso_error(self):
        # Missing POST data
        request = RequestFactory().post(
            reverse('saml_sso'), HTTP_HOST='idp.uw.edu')
        SessionMiddleware().process_request(request)
        request.session.save()

        view_instance = SSOView.as_view()
        response = view_instance(request)
        self.assertContains(response, 'SSO Error:', status_code=400)

        # Invalid SAMLResponse
        request = RequestFactory().post(
            reverse('saml_sso'), data={'SAMLResponse': None},
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
