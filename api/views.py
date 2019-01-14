from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import HttpResponseNotFound, JsonResponse
from .models import *
from logview.models import DnsLog,WebLog,UserSubDomain

# Create your views here.
def weblog(request, apikey, hashstr):
	user = ApiKey.objects.filter(key=apikey)
	if user:
		username = user[0].user.username
		# subdomain = UserSubDomain.objects.filter(user=user[0].user)[0].subdomain
		weblogs = WebLog.objects.filter(user=user[0].user).filter(path__contains=hashstr)
		data = []
		ret = {}
		if weblogs:
			for weblog in weblogs:
				data.append({'path': weblog.path, 'ip': weblog.ip, 'header': weblog.header, 'body': weblog.body})
			ret = {'status': 1, 'msg': '', 'total': len(weblogs), 'data': data}
		else:
			ret = {'status': 1, 'msg': '', 'total': 0, 'data': []}
	else:
		username = ''
		ret = {'status': -1, 'msg': 'api key not found!'}
	return JsonResponse(ret)



def dnslog(request, apikey, hashstr):
	user = ApiKey.objects.filter(key=apikey)
	if user:
		username = user[0].user.username
	else:
		username = ''
	return HttpResponse('OK')



def notfound(request):
	return HttpResponseNotFound('<h1>Page not found</h1>')
