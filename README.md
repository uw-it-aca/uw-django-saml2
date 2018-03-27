[![Build Status](https://api.travis-ci.org/uw-it-aca/uw-django-saml2.svg?branch=master)](https://travis-ci.org/uw-it-aca/uw-django-saml2)
[![Coverage Status](https://coveralls.io/repos/uw-it-aca/uw-django-saml2/badge.png?branch=master)](https://coveralls.io/r/uw-it-aca/uw-django-saml2?branch=master)

# uw-django-saml2

This project allows a Django app to be a SAML SP without running shibd and
apache mod_shib. The key dependency is OneLogin's [python3-saml package](https://github.com/onelogin/python3-saml). This app is targeted at python3.6, but python2.7 is also supported.

## Four steps to SAML

### Configure the LOGIN_URL

Configure the `saml_login` URL in `uw_saml.urls.py` to be the LOGIN_URL in your 
`project/settings.py`:

```
LOGIN_URL = 'uw_saml.views.LoginView'
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
url(r'^', include('uw_saml.urls')),
```

### Register your app as an SP

Register your app with the UW Service Provider Registry
