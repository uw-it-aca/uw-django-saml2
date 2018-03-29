from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic.base import View, TemplateView
from django.views.decorators.csrf import csrf_exempt
from uw_saml import DjangoSAML


class LoginView(View):
    def get(self, request, *args, **kwargs):
        auth = DjangoSAML(request)
        return HttpResponseRedirect(auth.login())


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        auth = DjangoSAML(request)

        name_id = request.session.get('samlNameId')
        session_index = request.session.get('samlSessionIndex')

        return HttpResponseRedirect(
            auth.logout(name_id=name_id, session_index=session_index))


@method_decorator(csrf_exempt, name='dispatch')
class SSOView(TemplateView):
    http_method_names = ['post']
    template_name = 'sso_error.html'

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

        request.session['samlUserdata'] = auth.get_attributes()
        request.session['samlNameId'] = auth.get_nameid()
        request.session['samlSessionIndex'] = auth.get_session_index()

        user = authenticate(request, remote_user=auth.get_nameid())
        if user is not None:
            login(request, user)

        return HttpResponseRedirect(auth.redirect_to())
