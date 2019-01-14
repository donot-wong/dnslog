from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ApiKey(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	key = models.CharField(max_length=40)
	status = models.IntegerField('api status')
	add_time = models.DateTimeField('time added', auto_now_add=True)
	class Meta:
		ordering = ['add_time']
