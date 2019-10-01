from django.conf.urls import url
from uw_saml.views import SAMLLoginView, SAMLLogoutView, SSOView


urlpatterns = [
    url(r'login$', SAMLLoginView.as_view(), name='saml_login'),
    url(r'logout$', SAMLLogoutView.as_view(), name='saml_logout'),
    url(r'sso$', SSOView.as_view(), name='saml_sso'),
]
