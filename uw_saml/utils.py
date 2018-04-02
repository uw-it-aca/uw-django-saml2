from django.conf import settings


def get_user(request):
    """
    Return the useri login stored in session.samlUserdata, identified in
    settings by either 'uwnetid' (default) or 'eppn'.
    """
    saml_data = request.session.get('samlUserdata')

    if saml_data is not None:
        user_attr = getattr(settings, 'SAML_USER_ATTRIBUTE', 'uwnetid')
        user = saml_data.get(user_attr, [])
        if len(user):
            return user[0]


def is_member_of_group(request, group_id):
    """
    Utility function that checks whether the user is a member of the group
    identified by the passed group_id.
    """
    saml_data = request.session.get('samlUserdata')

    if saml_data is not None:
        if group_id in saml_data.get('isMemberOf', []):
            return True

    return False
