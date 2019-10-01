from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic.base import View, TemplateView
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from uw_saml.auth import DjangoSAML


@method_decorator(never_cache, name='dispatch')
class SAMLLoginView(LoginView):
    template_name = 'mock_saml/login.html'

    def get(self, request, *args, **kwargs):
        mock_config = getattr(settings, 'UW_SAML_MOCK', False)
        if 'ENABLED' in mock_config and mock_config['ENABLED']:
            return super().get(request, *args, **kwargs)
        auth = DjangoSAML(request)
        return_url = request.GET.get(REDIRECT_FIELD_NAME)
        return HttpResponseRedirect(auth.login(return_to=return_url))


@method_decorator(never_cache, name='dispatch')
class SAMLLogoutView(LogoutView):
    template_name = 'mock_saml/logout.html'

    def get(self, request, *args, **kwargs):
        mock_config = getattr(settings, 'UW_SAML_MOCK', False)
        if 'ENABLED' in mock_config and mock_config['ENABLED']:
            return super().get(request, *args, **kwargs)
        auth = DjangoSAML(request)
        return HttpResponseRedirect(auth.logout())


@method_decorator(csrf_exempt, name='dispatch')
class SSOView(TemplateView):
    http_method_names = ['post']
    template_name = 'uw_saml/sso_error.html'

    def post(self, request, *args, **kwargs):
        auth = DjangoSAML(request)
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
