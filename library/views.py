from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.template import loader, Context
from library.forms import *
from django.contrib.auth.models import User
from django.template import RequestContext
from django.contrib.auth import logout as auth_logout

@login_required
def index(request):
    return HttpResponseRedirect('/home/')

@login_required
def home(request):
    t = loader.get_template('home.html')
    c = Context({'user': request.user})
    return HttpResponse(t.render(c))

def custom_login(request):
    from django.contrib.auth.views import login
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        return login(request)

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')

def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )
            username=form.cleaned_data['username']
            password=form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {
        'form': form
    })
    return render_to_response(
        'registration/register.html',
        variables
    )

@login_required()
def library(request):
    t = loader.get_template('library.html')
    c = Context({})
    return HttpResponse(t.render(c))