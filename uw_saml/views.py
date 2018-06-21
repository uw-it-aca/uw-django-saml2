from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic.base import View, TemplateView
from django.views.decorators.csrf import csrf_exempt
from uw_saml.auth import DjangoSAML


class LoginView(View):
    def get(self, request, *args, **kwargs):
        return_url = request.GET.get('next', '/')
        auth = DjangoSAML(request)
        return HttpResponseRedirect(auth.login(return_to=return_url))


class LogoutView(View):
    def get(self, request, *args, **kwargs):
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
            context = {'error_msg': ex, 'errors': auth.get_errors()}
            return self.render_to_response(context, status=400)

        errors = auth.get_errors()
        if len(errors):
            return self.render_to_response({'errors': errors}, status=500)

        return_url = request.POST.get('RelayState', '/')
        return HttpResponseRedirect(auth.redirect_to(return_url))
