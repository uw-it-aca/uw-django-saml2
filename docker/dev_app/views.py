from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from uw_saml.utils import is_member_of_group

# Create your views here.

@login_required
def index(request):
    if is_member_of_group(request, settings.UW_SAML_PERMISSIONS['perm2']):
        return HttpResponse("Hello, world. You have perm2.")
    else:
        return HttpResponse("Hello, world. You don't have perm2.")