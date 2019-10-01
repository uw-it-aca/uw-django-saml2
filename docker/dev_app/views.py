from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# Create your views here.

@login_required
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")