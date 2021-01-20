from django.urls import include, path

urlpatterns = [
    path('saml/', include('uw_saml.urls')),
]
