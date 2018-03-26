from django.conf.urls import include, url


urlpatterns = [
    url(r'^', include('uw_saml.urls')),
]
