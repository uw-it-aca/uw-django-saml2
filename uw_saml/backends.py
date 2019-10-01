from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend, RemoteUserBackend
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

UserModel = get_user_model()
SAMLBackend = None


class _SAMLModelBackend(ModelBackend):
    """
    Custom ModelBacked to provide onelogin SAML like behaviour
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        return super().authenticate(request, username, password, **kwargs)


class _SAMLRemoteUserBackend(RemoteUserBackend):
    """
    Custom RemoteUserBackend to handle onelogin SAML
    """

    def authenticate(self, request, remote_user):
        return super().authenticate(request, remote_user)


def load_perm_from_settings(config):
    if 'permissions' in config:
        for perm in config['permissions']:
            try:
                Permission.objects.get(codename=perm['codename'])
            except Permission.DoesNotExist:
                content_type = ContentType.objects.get_for_model(UserModel)
                Permission.objects.create(
                    codename=perm['codename'],
                    name=perm['name'],
                    content_type=content_type
                )


def load_settings():
    global SAMLBackend
    if getattr(settings, 'MOCK_SAML_AUTH', False):
        SAMLBackend = _SAMLModelBackend
    else:
        SAMLBackend = _SAMLRemoteUserBackend

    config = getattr(settings, 'UW_SAML_CONFIG', False)
    if config:
        load_perm_from_settings(config)
    else:
        ImproperlyConfigured('Missing "UW_SAML" dict in settings.py')


load_settings()
