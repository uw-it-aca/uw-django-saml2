from django.urls import include, re_path


urlpatterns = [
    re_path(r'^saml/', include('uw_saml.urls')),
]
