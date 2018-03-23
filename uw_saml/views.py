from django.http import HttpResponseRedirect
from django.views.generic.base import View
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


class SSOView(View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        auth = DjangoSAML(request)
        auth.process_response()

        errors = auth.get_errors()
        if errors:
            # TODO: handle login errors
            raise Exception(errors)

        return HttpResponseRedirect(
            auth.redirect_to(request.get('post_data').get('RelayState')))
