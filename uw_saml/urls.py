from django.conf import settings
from django.conf.urls import url
from uw_saml.views import LoginView, LogoutView, SSOView

urlpatterns = [
    url(r'login$', LoginView.as_view(), name='saml_login'),
    url(r'logout$', LogoutView.as_view(), name='saml_logout'),
    url(r'sso$', SSOView.as_view(), name='saml_sso'),
]

if (hasattr(settings, 'DJANGO_LOGIN_MOCK_SAML')):
    urlpatterns += [
        re_path(r'^mock_saml/login', LoginView.as_view(), name='mock_saml_login'),
        re_path(r'^mock_saml/logout', LogoutView.as_view(), name='mock_saml_logout'),
    ]
