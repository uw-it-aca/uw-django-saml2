# uw-django-saml2

[![Build Status](https://github.com/uw-it-aca/uw-django-saml2/workflows/tests/badge.svg?branch=master)](https://github.com/uw-it-aca/uw-django-saml2/actions)
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

from django.urls import reverse_lazy
LOGIN_URL = reverse_lazy('saml_login')
```

### Add your SP config

This app uses Django settings to configure the SP and IdP. Copy the `UW_SAML`
setting dict in `test/settings.py` to your `project/settings.py`.

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

To mock a SAML-authenticated session in your app, add the setting
`MOCK_SAML_ATTRIBUTES` to `project/settings.py`.  When this setting is
present, mocking takes precedence over the live SAML workflow.
The value of the setting is a SAML attribute set, representing the
desired attributes for the mocked user:

```
MOCK_SAML_ATTRIBUTES = {
    'uwnetid': ['javerage'],
    'affiliations': ['student', 'member'],
    'eppn': ['javerage@washington.edu'],
    'scopedAffiliations': ['student@washington.edu', 'member@washington.edu'],
    'isMemberOf': ['u_test_group', 'u_test_another_group'],
}
```

## Mocking a SAML login with a Django Login

To mock a SAML-authenticated session in your app change the
`AUTHENTICATION_BACKENDS` to include the mock backend.

```
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)
```

Also add the following:

```
DJANGO_LOGIN_MOCK_SAML = {
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

### Some Recommendations

#### Safetly setting login credentials

Replace:

`<some username>` with `os.getenv('MOCK_USERNAME', None)`,
`<some password>` with `os.getenv('MOCK_PASSWORD', None)`,
`<some email>` with `os.getenv('MOCK_EMAIL', None)`

Create a `.env` file and add this:

```
MOCK_USERNAME=<desired username>
MOCK_PASSWORD=<desired password>
MOCK_EMAIL=<desired emailid>
```

If you are using docker:

Add the following to your docker-compose inside the main app:

```
environment:
    MOCK_USERNAME: $MOCK_USERNAME
    MOCK_PASSWORD: $MOCK_PASSWORD
    MOCK_EMAIL: $MOCK_EMAIL
```

If you are using pipenv it should just work.

If you are using virtual env checkout https://pybit.es/persistent-environment-variables.html

#### Maintaining login session across server restarts

Make sure that:

`SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', get_random_secret_key())`

Create a `.env` file and add this:

```
DJANGO_SECRET_KEY = <50 character random value>
```

If you are using docker:

Add the following to your docker-compose inside the main app:

```
environment:
    DJANGO_SECRET_KEY: $DJANGO_SECRET_KEY
```

If you are using pipenv it should just work.

If you are using virtual env checkout https://pybit.es/persistent-environment-variables.html
