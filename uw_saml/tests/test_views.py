# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


import mock
import json
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory, override_settings
from uw_saml.views import LoginView, LogoutView, SSOView, MockSSOLoginView
from uw_saml.auth import OneLogin_Saml2_Auth, Django_Login_Mock_Saml2_Auth
from uw_saml.tests import (
    MOCK_SAML_ATTRIBUTES, UW_SAML_PERMISSIONS, DJANGO_LOGIN_MOCK_SAML)

CACHE_CONTROL = 'max-age=0, no-cache, no-store, must-revalidate'


class LoginViewTest(TestCase):
    def test_login(self):
        request = RequestFactory().get(
            reverse('saml_login'), HTTP_HOST='example.uw.edu')
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        response = middleware(request)
        request.session.save()

        view_instance = LoginView.as_view()
        response = view_instance(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn(settings.UW_SAML['idp']['singleSignOnService']['url'],
                      response.url)
        self.assertIn(CACHE_CONTROL, response.get('Cache-Control'))

    def test_missing_request_data(self):
        # Missing HTTP_HOST
        request = RequestFactory().get(reverse('saml_login'))
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        response = middleware(request)
        request.session.save()

        view_instance = LoginView.as_view()
        response = view_instance(request).render()
        self.assertContains(
            response, 'SSO Error: Login Failed', status_code=400)
        self.assertContains(
            response, 'Missing: &#39;HTTP_HOST&#39;', status_code=400,
            html=True)


class LogoutViewTest(TestCase):
    def test_logout(self):
        request = RequestFactory().get(
            reverse('saml_logout'), HTTP_HOST='example.uw.edu')
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        response = middleware(request)
        request.session['samlNameId'] = ''
        request.session['samlSessionIndex'] = ''
        request.session.save()

        view_instance = LogoutView.as_view()
        response = view_instance(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn(settings.UW_SAML['idp']['singleLogoutService']['url'],
                      response.url)
        self.assertIn(CACHE_CONTROL, response.get('Cache-Control'))

    def test_missing_request_data(self):
        # Missing HTTP_HOST
        request = RequestFactory().get(reverse('saml_logout'))
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        response = middleware(request)
        request.session['samlNameId'] = ''
        request.session['samlSessionIndex'] = ''
        request.session.save()

        view_instance = LogoutView.as_view()
        response = view_instance(request).render()
        self.assertContains(
            response, 'SSO Error: Logout Failed', status_code=400)
        self.assertContains(
            response, 'Missing: &#39;HTTP_HOST&#39;', status_code=400,
            html=True)


class SSOViewTest(TestCase):
    @mock.patch.object(OneLogin_Saml2_Auth, 'get_attributes')
    @mock.patch.object(OneLogin_Saml2_Auth, 'process_response')
    def test_sso(self, mock_process_response, mock_get_attributes):
        mock_get_attributes.return_value = MOCK_SAML_ATTRIBUTES

        request = RequestFactory().post(
            reverse('saml_sso'),
            data={'RelayState': '/private'},
            HTTP_HOST='example.uw.edu')
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        response = middleware(request)
        request.session.save()

        view_instance = SSOView.as_view()
        response = view_instance(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://example.uw.edu/private')


class SSOViewErrorTest(TestCase):
    def test_missing_request_data(self):
        # Missing HTTP_HOST
        request = RequestFactory().post(reverse('saml_sso'))
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        response = middleware(request)
        request.session.save()

        view_instance = SSOView.as_view()
        response = view_instance(request).render()
        self.assertContains(
            response, 'SSO Error: Login Failed', status_code=400)
        self.assertContains(
            response, 'Missing: &#39;HTTP_HOST&#39;', status_code=400,
            html=True)

    def test_missing_post_data(self):
        request = RequestFactory().post(
            reverse('saml_sso'), HTTP_HOST='example.uw.edu')
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        response = middleware(request)
        request.session.save()

        view_instance = SSOView.as_view()
        response = view_instance(request)
        self.assertContains(response, 'SSO Error:', status_code=400)

    def test_invalid_saml_response(self):
        request = RequestFactory().post(
            reverse('saml_sso'), data={'SAMLResponse': ''},
            HTTP_HOST='idp.uw.edu')
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        response = middleware(request)
        request.session.save()

        view_instance = SSOView.as_view()
        response = view_instance(request)
        self.assertContains(response, 'SSO Error:', status_code=400)

    def test_invalid_http_method(self):
        request = RequestFactory().get(
            reverse('saml_sso'), HTTP_HOST='idp.uw.edu')
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        response = middleware(request)
        request.session.save()

        view_instance = SSOView.as_view()
        response = view_instance(request)
        self.assertEqual(response.status_code, 405)


@override_settings(
    UW_SAML_PERMISSIONS=UW_SAML_PERMISSIONS,
    DJANGO_LOGIN_MOCK_SAML=DJANGO_LOGIN_MOCK_SAML,
    AUTHENTICATION_BACKENDS=('django.contrib.auth.backends.ModelBackend',)
)
class DjangoLoginViewTest(TestCase):
    def tearDown(self):
        User.objects.all().delete()

    def test_login_valid(self):
        request = RequestFactory().post(
            'login_django',
            data={'username': 'test_username', 'password': 'test_password'},
        )
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        response = middleware(request)
        request.session.save()
        request._dont_enforce_csrf_checks = True

        # Initalized so the users are loaded
        Django_Login_Mock_Saml2_Auth(request)
        response = MockSSOLoginView.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_login_invalid(self):
        request = RequestFactory().post(
            'login_django',
            data={
                'username': 'test_username',
                'password': 'test_wrong_password'
            },
        )
        get_response = mock.MagicMock()
        session_middleware = SessionMiddleware(get_response)
        response = session_middleware(request)
        authn_middleware = AuthenticationMiddleware(get_response)
        response = session_middleware(request)
        request._dont_enforce_csrf_checks = True

        # Initalized so the users are loaded
        Django_Login_Mock_Saml2_Auth(request)
        response = MockSSOLoginView.as_view()(request)
        self.assertEqual(response.status_code, 200)
