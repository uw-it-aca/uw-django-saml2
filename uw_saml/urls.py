from django.conf import settings
from django.conf.urls import re_path
from uw_saml.views import LoginView, LogoutView, SSOView, MockSSOLoginView


urlpatterns = [
    re_path(r'login$', LoginView.as_view(), name='saml_login'),
    re_path(r'logout$', LogoutView.as_view(), name='saml_logout'),
    re_path(r'sso$', SSOView.as_view(), name='saml_sso'),
]

if (hasattr(settings, 'DJANGO_LOGIN_MOCK_SAML')):
    urlpatterns.append(re_path(
        r'^login_django$', MockSSOLoginView.as_view(), name='login_django')
    )
