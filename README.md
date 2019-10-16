# uw-django-saml2

[![Build Status](https://api.travis-ci.org/uw-it-aca/uw-django-saml2.svg?branch=master)](https://travis-ci.org/uw-it-aca/uw-django-saml2)
[![Coverage Status](https://coveralls.io/repos/github/uw-it-aca/uw-django-saml2/badge.svg?branch=master)](https://coveralls.io/github/uw-it-aca/uw-django-saml2?branch=master)
[![PyPi Version](https://img.shields.io/pypi/v/uw-django-saml2.svg)](https://pypi.python.org/pypi/uw-django-saml2)
![Python versions](https://img.shields.io/pypi/pyversions/uw-django-saml2.svg)


This app allows a Django project to be a SAML SP without running shibd and
apache mod_shib. The key dependency is OneLogin's [python3-saml package](https://github.com/onelogin/python3-saml).
For easier development and testing, the app also supports configuring a mocked
SAML-authenticated session.

## Four steps to SAML

### Configure the LOGIN_URL and required settings

Add required settings, and configure the `saml_login` URL in `uw_saml.urls.py` to be the LOGIN_URL in your
`project/settings.py`:

```
INSTALLED_APPS = ['uw_saml',]

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.RemoteUserBackend',]

MIDDLEWARE = ['django.contrib.auth.middleware.PersistentRemoteUserMiddleware',]

from django.core.urlresolvers import reverse_lazy
LOGIN_URL = reverse_lazy('saml_login')
```

### Add your SP config

This app uses Django settings to configure the SP and IdP. Copy the `UW_SAML`
setting dict in `travis-ci/settings.py` to your `project/settings.py`.

You will need to update these settings to the correct values for your SP:

`sp.entityId`
`sp.x509cert`
`sp.assertionConsumerService.url`
`sp.singleLogoutService.url`

Also, be sure to set `strict: True` for production usage!

### Include the uw_saml URLs

Add the uw_saml URLs to your `project/urls.py`:

```
url(r'^saml/', include('uw_saml.urls')),
```

### Register your app as an SP

Register your app with the UW Service Provider Registry

## Mocking a SAML login

To mock a SAML-authenticated session in your app change the
`AUTHENTICATION_BACKENDS` to only include the mock backend.

```
AUTHENTICATION_BACKENDS = ('uw_saml.backends.SamlMockModelBackend',)
```

Also add the following:

```
UW_SAML_MOCK = {
    'NAME_ID': 'mock-nameid',
    'SESSION_INDEX': 'mock-session',
    'SAML_USERS': [
        {
            "username": <some username>,
            "password": <some password>,
            "email": <some email>,
            "MOCK_ATTRIBUTES" : {
                'uwnetid': [<some username>],
                'affiliations': ['student', 'member'],
                'eppn': ['javerage@washington.edu'],
                'scopedAffiliations': ['student@washington.edu', 'member@washington.edu'],
                'isMemberOf': [
                    'u_test_group', 'u_test_another_group'
                ],
            }
        }
    ]
}
```

replace `<some username>`, `<some password>`, `<some email>` with the values you want.
You will use these to login when in mock mode. You can add more mock users by appending
to the `SAML_USERS` array in `UW_SAML_MOCK`.

## Running the sample SAML mock login app.

A sample application with mocking turned is provided in the repo.
To run the demo create a file named `.env` locally.
Add the following to the file:

```
MOCK_USERNAME=<some username>
MOCK_PASSWORD=<some password>
MOCK_EMAIL=<some email>
```

replace `<some username>`, `<some password>`, `<some email>` with the values you want.
You will use these to login to the sample app.

run `docker-compose up` to run the sample app. After the django server is running navigate
to `localhost:8000/dev_app/`

you should be redirected to the login page. You can use the `<some username>`, `<some password>`
values to login now.
