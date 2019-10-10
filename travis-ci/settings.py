import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

DEBUG = True

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.RemoteUserBackend',)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'uw_saml'
]

ROOT_URLCONF = 'travis-ci.urls'

ALLOWED_HOSTS = [
    'example.uw.edu'
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]

WSGI_APPLICATION = 'travis-ci.wsgi.application'

from django.urls import reverse_lazy
LOGIN_URL = reverse_lazy('saml_login')

UW_SAML = {
    'strict': False,
    'debug': True,
    'sp': {
        'entityId': 'https://example.uw.edu/saml2',
        'assertionConsumerService': {
            'url': 'https://example.uw.edu/saml/sso',
            'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'
        },
        'singleLogoutService': {
            'url': 'https://example.uw.edu/saml/logout',
            'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
        },
        'NameIDFormat': 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified',
        'x509cert': '',
        # for encrypted saml assertions uncomment and add the private key
        # 'privateKey': '',
    },
    'idp': {
        'entityId': 'urn:mace:incommon:washington.edu',
        'singleSignOnService': {
            'url': 'https://idp.u.washington.edu/idp/profile/SAML2/Redirect/SSO',
            'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
        },
        'singleLogoutService': {
            'url': 'https://idp.u.washington.edu/idp/logout',
            'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
        },
        'x509cert': '',
    },
    'security': {
        # for encrypted saml assertions
        # 'wantAssertionsEncrypted': True,
        # for 2FA uncomment this line
        # 'requestedAuthnContext':  ['urn:oasis:names:tc:SAML:2.0:ac:classes:TimeSyncToken']
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

STATIC_URL = '/static/'
