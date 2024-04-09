# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.test import TestCase, RequestFactory
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from uw_saml.decorators import group_required
import mock


@method_decorator(group_required('u_test_group'), name='dispatch')
class GroupRequiredView(View):
    def get(request, *args, **kwargs):
        return HttpResponse('OK')


class DecoratorTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('/')
        self.request.user = User()
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        response = middleware(self.request)
        self.request.session.save()

    def test_group_required_noauth(self):
        self.request.user = AnonymousUser()

        view_instance = GroupRequiredView.as_view()
        response = view_instance(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('%s?next=/' % settings.LOGIN_URL, response.url,
                      'Login required')

    def test_group_required_nogroups(self):
        self.request.session['samlUserdata'] = {}

        view_instance = GroupRequiredView.as_view()
        response = view_instance(self.request)
        self.assertEqual(response.status_code, 401)

    def test_group_required_withgroups(self):
        self.request.session['samlUserdata'] = {
            'isMemberOf': ['u_wrong_group']}

        view_instance = GroupRequiredView.as_view()
        response = view_instance(self.request)
        self.assertEqual(response.status_code, 401)

    def test_group_required_ok(self):
        self.request.session['samlUserdata'] = {
            'isMemberOf': ['u_wrong_group', 'u_test_group']}

        view_instance = GroupRequiredView.as_view()
        response = view_instance(self.request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'OK')
