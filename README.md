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

### Configure the LOGIN_URL

Configure the `saml_login` URL in `uw_saml.urls.py` to be the LOGIN_URL in your
`project/settings.py`:

```
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

## Other required settings

```
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.RemoteUserBackend',)
```
