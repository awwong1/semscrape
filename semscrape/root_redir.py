from django.conf.urls import url
from django.http import HttpResponseRedirect


def redirect_to_index(request):
    print("why?")
    return HttpResponseRedirect("/app/index.html")


urlpatterns = [url(r"^$", redirect_to_index)]
