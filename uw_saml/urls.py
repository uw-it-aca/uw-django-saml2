from django.conf.urls import url
from uw_saml.views import LoginView, LogoutView, SSOView


urlpatterns = [
    url(r'login$', LoginView.as_view(), name='saml_login'),
    url(r'logout$', LogoutView.as_view(), name='saml_logout'),
    url(r'sso$', SSOView.as_view(), name='saml_sso'),
]
