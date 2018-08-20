from django.shortcuts import reverse
from django.http import HttpResponseRedirect


def index(request):
    return HttpResponseRedirect(reverse('bazaar:index'))
