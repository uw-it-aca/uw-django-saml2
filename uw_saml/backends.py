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
        user = super().authenticate(request, remote_user)
        for perm in request.session['samlUserdata']['isMemberOf']:
            user.user_permissions.add(
                Permission.objects.get(codename=perm)
            )
        user.save()
        return user


def load_perm_from_settings(config):
    if 'PERMISSIONS' in config:
        for perm in config['PERMISSIONS']:
            try:
                Permission.objects.get(codename=perm['codename'])
            except Permission.DoesNotExist:
                content_type = ContentType.objects.get_for_model(UserModel)
                Permission.objects.create(
                    codename=perm['codename'],
                    name=perm['name'],
                    content_type=content_type
                )


def load_users_from_settings(mock_config):
    if 'SAML_USERS' in mock_config:
        for user in mock_config['SAML_USERS']:
            try:
                UserModel.objects.get(username=user["username"])
            except UserModel.DoesNotExist:
                new_user = UserModel.objects.create_user(
                    user["username"],
                    user['email'],
                    user["password"]
                )
                for perm in user["permissions"]:
                    new_user.user_permissions.add(
                        Permission.objects.get(codename=perm)
                    )
                new_user.save()


def load_settings():
    config = getattr(settings, 'UW_SAML_CONFIG', False)
    if config:
        load_perm_from_settings(config)
    else:
        ImproperlyConfigured('Missing "UW_SAML" dict in settings.py')

    mock_config = getattr(settings, 'UW_SAML_MOCK', False)
    global SAMLBackend
    if 'ENABLED' in mock_config and mock_config['ENABLED']:
        SAMLBackend = _SAMLModelBackend
        load_users_from_settings(mock_config)
    else:
        SAMLBackend = _SAMLRemoteUserBackend


load_settings()
