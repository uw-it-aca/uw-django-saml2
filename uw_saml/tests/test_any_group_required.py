from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.test import TestCase, RequestFactory
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from uw_saml.decorators import any_group_required

GROUPS = ['u_test_group_a', 'u_test_group_b']


@method_decorator(
        any_group_required(*GROUPS),
        name='dispatch')
class AnyGroupRequiredView(View):
    def get(request, *args, **kwargs):
        return HttpResponse('OK')


class DecoratorTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('/')
        self.request.user = User()
        SessionMiddleware().process_request(self.request)
        self.request.session.save()

    def test_any_group_required_noauth(self):
        self.request.user = AnonymousUser()

        view_instance = AnyGroupRequiredView.as_view()
        response = view_instance(self.request)
        self.assertEquals(response.status_code, 302)
        self.assertIn('%s?next=/' % settings.LOGIN_URL, response.url,
                      'Login required')

    def test_any_group_required_nogroups(self):
        self.request.session['samlUserdata'] = {}

        view_instance = AnyGroupRequiredView.as_view()
        response = view_instance(self.request)
        self.assertEquals(response.status_code, 401)

    def test_any_group_required_withgroups(self):
        self.request.session['samlUserdata'] = {
            'isMemberOf': ['u_wrong_group']}

        view_instance = AnyGroupRequiredView.as_view()
        response = view_instance(self.request)
        self.assertEquals(response.status_code, 401)

    def test_any_group_required_ok(self):
        for group in GROUPS:
            self.request.session['samlUserdata'] = {
                'isMemberOf': ['u_wrong_group', group]}

            view_instance = AnyGroupRequiredView.as_view()
            response = view_instance(self.request)
            self.assertEquals(response.status_code, 200)
            self.assertEquals(response.content, b'OK')

    def test_any_group_required_one(self):
        for group in GROUPS:
            self.request.session['samlUserdata'] = {
                'isMemberOf': [group]}

            view_instance = AnyGroupRequiredView.as_view()
            response = view_instance(self.request)
            self.assertEquals(response.status_code, 200)

    def test_any_group_required_all(self):
        self.request.session['samlUserdata'] = {
            'isMemberOf': GROUPS}

        view_instance = AnyGroupRequiredView.as_view()
        response = view_instance(self.request)
        self.assertEquals(response.status_code, 200)
