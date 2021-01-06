import urllib
from django.http import HttpResponseRedirect

def index(request):
    return HttpResponseRedirect(f'{urllib.parse.urljoin("https://yata.yt", request.path)}{f"?{urllib.parse.urlencode(request.GET)}" if len(request.GET) else ""}')
