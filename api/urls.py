from django.urls import path, re_path

from . import views

urlpatterns = [
	path('<apikey>/weblog/<hashstr>', views.weblog),
	path('<apikey>/dnslog/<hashstr>', views.dnslog),
	re_path('.*', views.notfound),
]