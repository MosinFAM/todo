from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            return HttpResponse(f'Account {username} was created!')
        else:
            return HttpResponse('Registration error: ' + str(form.errors))
    return HttpResponseNotAllowed(['POST'])


@csrf_exempt
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return HttpResponse(f'Welcome, {user.username}!')
        else:
            return HttpResponse('Login error: ' + str(form.errors))
    return HttpResponseNotAllowed(['POST'])


@csrf_exempt
@login_required
def logout_view(request):
    logout(request)
    return HttpResponse('You logged out! You can login now!')


def my_user(request):
    user = request.user
    if user.is_authenticated:
        return HttpResponse(f'You are {user.username}')
    return HttpResponse('You need to login')
