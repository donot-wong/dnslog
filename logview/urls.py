from django.urls import path,re_path

from . import views

urlpatterns = [
	path('', views.index),
	path('index', views.index),
	path('login', views.index, name='index'),
	path('main', views.main, name='main'),
	path('logout', views.logout_view, name='logout'),
	path('weblog', views.weblog, name='weblog'),
	path('dnslog', views.dnslog, name='dnslog'),
	path('manage', views.manage, name='manage'),
	path('manage/add', views.manage_user_add, name='manage_user_add'),
	path('manage/del', views.manage_user_del, name='manage_user_del'),
	re_path('.*', views.index),
]