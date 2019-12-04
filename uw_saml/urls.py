from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.views import LoginView as MockLoginView, \
    LogoutView as MockLogoutView
from uw_saml.views import LoginView, LogoutView, SSOView

urlpatterns = []

if (hasattr(settings, 'DJANGO_LOGIN_MOCK_SAML')):
    urlpatterns += [
        url(
            r'^mock_login$',
            MockLoginView.as_view(),
            name='mock_saml_login'
        ),
        url(
            r'^mock_logout$',
            MockLogoutView.as_view(),
            name='mock_saml_logout'
        ),
    ]

urlpatterns += [
    url(r'login$', LoginView.as_view(), name='saml_login'),
    url(r'logout$', LogoutView.as_view(), name='saml_logout'),
    url(r'sso$', SSOView.as_view(), name='saml_sso'),
]
