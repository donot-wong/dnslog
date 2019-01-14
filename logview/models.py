from django.db import models
from django.contrib.auth.models import User


class WebLog(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	ip = models.GenericIPAddressField('remote_addr')
	path = models.TextField('path')
	header = models.TextField('header')
	body = models.TextField('body')
	log_time = models.DateTimeField('time loged', auto_now_add=True)
	class Meta:
		ordering = ['log_time']


class DnsLog(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	host = models.TextField('host')
	type = models.TextField('dns type')
	log_time = models.DateTimeField('time loged', auto_now_add=True)
	class Meta:
		ordering = ['log_time']


class UserSubDomain(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	subdomain = models.CharField(max_length=128)
	status = models.IntegerField('status')
	add_time = models.DateTimeField('time added', auto_now_add=True)
	class Meta:
		ordering = ['add_time']
