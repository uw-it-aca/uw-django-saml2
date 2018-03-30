from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def group_required(group_id):
    """
    A decorator for views that checks whether the user is a member of the group
    identified by the passed group_id. Calls login_required if the user is not
    authenticated.
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            saml_data = request.session.get('samlUserdata')

            if saml_data is not None:
                group_urn = 'urn:mace:washington.edu:groups:%s' % group_id
                if group_urn in saml_data.get('isMemberOf', []):
                    return view_func(request, *args, **kwargs)

            return render(request, 'access_denied.html', status=401)

        return login_required(function=wrapper)

    return decorator
