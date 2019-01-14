from django.shortcuts import render,redirect
from django.shortcuts import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.http import HttpResponseNotFound, HttpResponseRedirect
from dnslog import settings
from hashlib import sha512
import random
import string
from api.models import *
from .models import *


def index(request):
	host = request.get_host()
	if ':' in host:
		host = host.split(':')[0]
	else:
		pass
	if host != settings.ADMIN_DOMAIN: # 非后台
		headers = ''
		for header, value in request.META.items():
			if not header.startswith('HTTP'):
				continue
			header = '-'.join([h.capitalize() for h in header[5:].lower().split('_')])
			headers += '{}: {}\n'.format(header, value)
		method = request.method
		path = request.get_full_path()
		body = request.body or ' '
		realip = request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR')
		subdomain = host.replace(settings.DNS_DOMAIN, '')
		if subdomain:
			domains = subdomain.split('.')
			usersubdomain = ''
			if len(domains) >= 2:
				# usersubdomain = domains[-2]
				usersubdomain = UserSubDomain.objects.filter(subdomain=domains[-2])
				if usersubdomain:
					weblog = WebLog(user=usersubdomain[0].user, ip=realip, path=path, header=headers, body=body)
					weblog.save()
					return HttpResponse('good boy')
		return HttpResponse('bad boy')
	else:
		pass


	if request.method == 'GET':
		return render(request, 'logview/login.html')
	elif request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			login(request, user)
			# return HttpResponse("Login Success!")
			return redirect('/logview/dnslog')
		else:
			return render(request, 'logview/login.html', {'error': 'username or password error!'})
			return HttpResponse("Login Failed!")
	else:
		return HttpResponseNotAllowed



@login_required(login_url='/logview/login')
def main(request):
	# return HttpResponse("Ok")
	return render(request, 'logview/views.html')


@login_required(login_url='/logview/login')
def logout_view(request):
	logout(request)
	return redirect('/logview/')



@login_required(login_url='/logview/login')
def selfinfo(request):
	user = request.user
	subdomain = UserSubDomain.objects.filter(user=user)[0].subdomain
	apikey = ApiKey.objects.filter(user=user)[0].key
	vardict = {}
	vardict['type'] = 'info'
	vardict['subdomain'] = subdomain
	vardict['apikey'] = apikey
	return render(request, 'logview/views.html', vardict)



@login_required(login_url='/logview/login')
def dnslog(request):
	user = request.user
	vardict = {}
	dnspage = getpage(request.GET.get("dnspage", 1))
	paginator = Paginator(DnsLog.objects.filter(user=user), 10)
	try:
		dnslogs = paginator.page(dnspage)
	except(EmptyPage, InvalidPage, PageNotAnInteger):
		dnspage = paginator.num_pages
		dnslogs = paginator.page(paginator.num_pages)
	vardict['type'] = 'dns'
	vardict['dnspage'] = dnspage
	vardict['pagerange'] = paginator.page_range
	vardict['dnslogs'] = dnslogs
	vardict['numpages'] = paginator.num_pages

	usersubdomain = UserSubDomain.objects.filter(user=user)[0].subdomain
	vardict['userdomain'] = usersubdomain + '.' + settings.DNS_DOMAIN

	vardict['udomain'] = str(usersubdomain)
	vardict['admindomain'] = str(settings.ADMIN_DOMAIN)
	vardict['apikey'] = ApiKey.objects.filter(user=user)[0].key

	return render(request, 'logview/views.html', vardict)



@login_required(login_url='/logview/login')
def weblog(request):
	user = request.user
	vardict = {}
	webpage = getpage(request.GET.get("webpage", 1))
	paginator = Paginator(WebLog.objects.filter(user=user), 10)
	try:
		weblogs = paginator.page(webpage)
	except(EmptyPage, InvalidPage, PageNotAnInteger):
		webpage = paginator.num_pages
		weblogs = paginator.page(paginator.num_pages)
	# print(weblogs)
	vardict['type'] = 'web'
	vardict['webpage'] = webpage
	vardict['pagerange'] = paginator.page_range
	vardict['weblogs'] = weblogs
	vardict['numpages'] = paginator.num_pages

	usersubdomain = UserSubDomain.objects.filter(user=user)[0].subdomain
	vardict['userdomain'] = usersubdomain + '.' + settings.DNS_DOMAIN

	vardict['udomain'] = str(usersubdomain)
	vardict['admindomain'] = str(settings.ADMIN_DOMAIN)
	vardict['apikey'] = ApiKey.objects.filter(user=user)[0].key

	return render(request, 'logview/views.html', vardict)


def getpage(p):
    try:
        page = int(p)
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    return page


@login_required(login_url='/logview/login')
def api_add(request):
	randstr = ''.join(random.sample(string.ascii_letters + string.digits, 8))
	sh = sha512()
	sh.update(randstr.encode('utf-8'))
	key = sh.hexdigest()


@login_required(login_url='/logview/login')
def clear(request, type):
	user = request.user
	if type == 'dnslog':
		DnsLog.objects.filter(user=user).delete()
		return HttpResponseRedirect('/logview/dnslog')
	elif type == 'weblog':
		WebLog.objects.filter(user=user).delete()
		return HttpResponseRedirect('/logview/weblog')
	else:
		return HttpResponseNotFound('Not Found')




