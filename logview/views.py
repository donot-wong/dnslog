from django.shortcuts import render,redirect
from django.shortcuts import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.http import HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from dnslog import settings
from hashlib import sha1
import re
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


def genapikey():
	randstr = ''.join(random.sample(string.ascii_letters + string.digits, 8))
	sh = sha1()
	sh.update(randstr.encode('utf-8'))
	key = sh.hexdigest()
	return key


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

@login_required(login_url='/logview/login')
def manage(request):
	user = request.user
	if user.is_superuser:
		vardict = {}
		userpage = getpage(request.GET.get("userpage", 1))
		paginator = Paginator(UserSubDomain.objects.all(), 10)
		try:
			users = paginator.page(userpage)
		except (EmptyPage, InvalidPage, PageNotAnInteger):
			userpage = paginator.num_pages
			users = paginator.page(paginator.num_pages)
		vardict['type'] = 'manage'
		vardict['userpage'] = userpage
		vardict['pagerange'] = paginator.page_range
		vardict['users'] = users
		vardict['numpages'] = paginator.num_pages

		return render(request, 'logview/manage.html', vardict)
	else:
		return redirect('/logview/dnslog')


@login_required(login_url='/logview/login')
def manage_user_del(request):
	userid = request.POST['id']
	user = User.objects.filter(id=userid)
	try:
		if len(user) == 1:
			user[0].delete()
			ret = {'status': 1, 'msg': 'Ok'}
		else:
			ret = {'status': -1, 'msg': 'user error!'}
	except Exception as e:
		ret = {'status': -1, 'msg': e}
	return JsonResponse(ret)


@login_required(login_url='/logview/login')
def manage_user_add(request):
	user = request.user
	if user.is_superuser:
		username = request.POST['username']
		password = request.POST['password']
		subdomain = request.POST['subdomain']

		# form data check
		if not re.match(r'^[a-zA-Z0-9]+$',  username):
			ret = {'status': -1, 'msg': 'username not vaild!'}
			return JsonResponse(ret)
		if password == '':
			ret = {'status': -1, 'msg': 'password can not be empty!'}
			return JsonResponse(ret)

		if subdomain == '':
			randomStr = ''.join(random.sample(string.ascii_letters + string.digits, 5))
			checkSubdomain = UserSubDomain.objects.filter(subdomain=randomStr)
			while checkSubdomain:
				randomStr = ''.join(random.sample(string.ascii_letters + string.digits, 5))
			subdomain = randomStr
		else:
			checkSubdomain = UserSubDomain.objects.filter(subdomain=subdomain)
			if checkSubdomain:
				ret = {'status': -1, 'msg': 'subdomain already exist!'}
				return JsonResponse(ret)


		# infomation exist check
		checkUser = User.objects.filter(username=username)
		if checkUser:
			ret = {'status': -1, 'msg': 'username already exist!'}
			return JsonResponse(ret)

		# database
		from django.db import transaction
		try:
			with transaction.atomic():
				adduser = User.objects.create_user(username=username, password=password)
				usersubdomain = UserSubDomain(user=adduser, subdomain=subdomain, status=1)
				apikey = ApiKey(user=adduser, key=genapikey(), status=1)
				usersubdomain.save()
				apikey.save()
				ret = {'status': 1, 'msg': 'Ok'}
				return JsonResponse(ret)
		except Exception as e:
			# print(e)
			ret = {'status': 1, 'msg': e}
			return JsonResponse(ret)
	else:
		return redirect('/logview/dnslog')
