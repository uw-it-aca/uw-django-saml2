from django.conf.urls import url
from uw_saml.views import LoginView, LogoutView, SSOView


urlpatterns = [
    url(r'saml/login$', LoginView.as_view(), name='saml_login'),
    url(r'saml/logout$', LogoutView.as_view(), name='saml_logout'),
    url(r'Shibboleth.sso/SAML2/POST$', SSOView.as_view(), name='saml_sso'),
]
