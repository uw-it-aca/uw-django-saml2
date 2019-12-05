from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import LoginView as DjangoLoginView,\
    LogoutView as DjangoLogoutView
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.utils.decorators import method_decorator
from django.views.generic.base import View, TemplateView
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy, resolve
from uw_saml.auth import DjangoSAML


class UWSAMLView(TemplateView):
    template_name = 'uw_saml/sso_error.html'


@method_decorator(never_cache, name='dispatch')
class LoginView(UWSAMLView):
    def get(self, request, *args, **kwargs):
        return_url = request.GET.get(REDIRECT_FIELD_NAME)
        try:
            auth = DjangoSAML(request)
            return HttpResponseRedirect(auth.login(return_to=return_url))
        except KeyError as ex:
            context = {'errors': ['Missing: {}'.format(ex)]}
            return self.render_to_response(context, status=400)


@method_decorator(never_cache, name='dispatch')
class LogoutView(UWSAMLView):
    def get(self, request, *args, **kwargs):
        try:
            auth = DjangoSAML(request)
            return HttpResponseRedirect(auth.logout())
        except KeyError as ex:
            context = {'error_msg': 'Logout Failed',
                       'errors': ['Missing: {}'.format(ex)]}
            return self.render_to_response(context, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class SSOView(UWSAMLView):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            auth = DjangoSAML(request)
        except KeyError as ex:
            context = {'errors': ['Missing: {}'.format(ex)]}
            return self.render_to_response(context, status=400)

        try:
            auth.process_response()
        except Exception as ex:
            context = {'error_msg': str(ex),
                       'errors': auth.get_errors()}
            return self.render_to_response(context, status=400)

        errors = auth.get_errors()
        if len(errors):
            return self.render_to_response({'errors': errors}, status=500)

        return_url = request.POST.get('RelayState')
        return HttpResponseRedirect(auth.redirect_to(return_url))


@method_decorator(csrf_exempt, name='dispatch')
class MockSSOLogin(DjangoLoginView):
    def post(self, request, *args, **kwargs):
        response = super().post(self, request, *args, **kwargs)
        if response.status_code == 302:
            saml_sso_url = reverse_lazy('saml_sso')
            manufactured_request = RequestFactory().post(
                saml_sso_url,
                data={"RelayState": self.get_redirect_url()}
            )
            manufactured_request.user = request.user
            manufactured_request.session = request.session
            resolve(saml_sso_url).func(manufactured_request)
        return response
