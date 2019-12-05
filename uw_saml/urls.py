from django.conf import settings
from django.conf.urls import url
from uw_saml.views import LoginView, LogoutView, SSOView, \
    MockSSOLogin

urlpatterns = []

if (hasattr(settings, 'DJANGO_LOGIN_MOCK_SAML')):
    urlpatterns += [
        url(
            r'^mock_sso_login$',
            MockSSOLogin.as_view(template_name='uw_saml/mock/login.html'),
            name='mock_sso_login'
        ),
    ]

urlpatterns += [
    url(r'login$', LoginView.as_view(), name='saml_login'),
    url(r'logout$', LogoutView.as_view(), name='saml_logout'),
    url(r'sso$', SSOView.as_view(), name='saml_sso'),
]
