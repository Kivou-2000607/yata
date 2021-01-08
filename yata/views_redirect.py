import urllib
from django.http import HttpResponseRedirect
from django.shortcuts import render

# def index(request):
#     return HttpResponseRedirect(f'{urllib.parse.urljoin("https://yata.yt", request.path)}{f"?{urllib.parse.urlencode(request.GET)}" if len(request.GET) else ""}')

def index(request):
    return render(request, 'redirect.html')
