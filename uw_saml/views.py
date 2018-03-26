from django.http import HttpResponseRedirect
from django.views.generic.base import View, TemplateView
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


class SSOView(TemplateView):
    http_method_names = ['post']
    template_name = 'sso_error.html'

    def post(self, request, *args, **kwargs):
        auth = DjangoSAML(request)

        try:
            auth.process_response()
        except Exception as ex:
            context = {
                'name': ex,
                'errors': auth.get_errors()
            }
            return self.render_to_response(context, status=500)

        return HttpResponseRedirect(
            auth.redirect_to(request.get('post_data').get('RelayState')))
