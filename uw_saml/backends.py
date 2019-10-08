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
        a_user = super().authenticate(request, username, password, **kwargs)
        
        mock_config = getattr(settings, 'UW_SAML_MOCK', False)
        if 'ENABLED' in mock_config and mock_config['ENABLED'] and a_user:
            for user in mock_config['SAML_USERS']:
                if user['username'] == username:
                    request.session['samlUserdata'] = user['MOCK_ATTRIBUTES']
                    request.session['samlNameId'] = mock_config['NAME_ID']
                    request.session['samlSessionIndex'] = "{}-{}".format(
                        mock_config['SESSION_INDEX'],
                        username
                    )
        else:
            raise ImproperlyConfigured('SAML_MOCK change needs a restart')
        
        return a_user


def load_users_from_settings(mock_config):
    if 'SAML_USERS' in mock_config:
        for user in mock_config['SAML_USERS']:
            try:
                UserModel.objects.get_or_create(username=user["username"])
            except UserModel.DoesNotExist:
                new_user = UserModel.objects.create_user(
                    user["username"],
                    user['email'],
                    user["password"]
                )


def load_settings():
    mock_config = getattr(settings, 'UW_SAML_MOCK', False)
    global SAMLBackend
    if 'ENABLED' in mock_config and mock_config['ENABLED']:
        SAMLBackend = _SAMLModelBackend
        load_users_from_settings(mock_config)
    else:
        SAMLBackend = RemoteUserBackend


load_settings()
