from django.urls import path
from .views import test
from django.contrib.auth import views as auth_views

app_name = 'chat'

urlpatterns = [
	path('', test, name='test'),
]