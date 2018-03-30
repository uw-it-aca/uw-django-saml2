def is_member_of_group(request, group_id):
    """
    Utility function that checks whether the user is a member of the group
    identified by the passed group_id.
    """
    saml_data = request.session.get('samlUserdata')

    if saml_data is not None:
        group_urn = 'urn:mace:washington.edu:groups:%s' % group_id
        if group_urn in saml_data.get('isMemberOf', []):
            return True

    return False
