from django.conf.urls import url
from django.contrib.auth import get_backends
from django.contrib.auth.views import LoginView, LogoutView

from uw_saml.views import SAMLLoginView, SAMLLogoutView, SSOView
from uw_saml.backends import SamlMockModelBackend


def _isMockSamlBackend():
    for backend in get_backends():
        if (isinstance(backend, SamlMockModelBackend)):
            return True
    return False


urlpatterns = [
    url(
        r'login$',
        (LoginView.as_view(template_name='mock_saml/login.html')
         if _isMockSamlBackend()
         else SAMLLoginView.as_view()),
        name='saml_login'
    ),
    url(
        r'logout$',
        (LogoutView.as_view(template_name='mock_saml/logout.html')
         if _isMockSamlBackend()
         else SAMLLogoutView.as_view()),
        name='saml_logout'
    ),
    url(r'sso$', SSOView.as_view(), name='saml_sso'),
]
