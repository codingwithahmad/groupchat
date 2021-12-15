import json
from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.http import HttpResponse
from .forms import UserRegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def register(request):

	if request.method == 'POST':
		form = UserRegisterForm(request.POST)

		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')


			user = authenticate(username=username, password=password)

			if user is not None:
				if user.is_active:
					login(request, user)
					return redirect('chat:index')
	else:
		form = UserRegisterForm()

	return render(request, "chat/register.html", {"form": form})


@login_required
def index(request):
	current_user = request.user
	return render(request, 'chat/index.html', {'member': current_user.member_set.all()})