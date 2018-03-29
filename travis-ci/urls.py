from django.conf.urls import include, url


urlpatterns = [
    url(r'^saml/', include('uw_saml.urls')),
]
