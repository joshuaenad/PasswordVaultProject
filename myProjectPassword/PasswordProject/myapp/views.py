from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import  authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import redirect, render
from mechanize import Browser

from .forms import MyUserCreationForm, PasswordForm
from .models import Password

import favicon


br = Browser()
br.set_handle_robots(False)
fernet = Fernet(settings.KEY)


def login_page(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist.')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist.')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


@login_required(login_url='/login/')
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    passwords_search = Password.objects.filter(
        Q(name__icontains=q)|
        Q(username__icontains=q)
        ).filter(user=request.user)
    password = Password.objects.all()[0:5]
    password_count = passwords_search.count()

    if request.user.is_authenticated:
        passwords = Password.objects.all().filter(user=request.user).filter(
            Q(name__icontains=q)|
            Q(username__icontains=q)
            )
        for password in passwords:
            password.password = fernet.encrypt(password.password.encode())

    return render(request, 'base/home.html', {'passwords_search':passwords_search, 'password':password,
    "passwords":passwords, 'password_count': password_count})


def logout_user(request):
    msg = f"{request.user}. You logged out."
    logout(request)
    messages.success(request, msg)
    return redirect('home')


def register_page(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            msg = f"Thank you for signing up."
            login(request, user)
            messages.success(request, msg)
            return redirect('home')
        else:
            messages.error(request, 'An error occured on registration.')

    context = {'form': form}
    return render(request, 'base/login_register.html', context)


@login_required(login_url='/login/')
def create_password(request):
    form = PasswordForm()
    password = Password.objects.all()

    if request.method == "POST":
        url = request.POST.get("url")
        username = request.POST.get("username")
        password = request.POST.get("password")
        #ecrypt data
        encrypted_url = url
        encrypted_username = username
        encrypted_password = fernet.encrypt(password.encode())
        #get title of the website
        try:
            br.open(url)
            title = br.title()
        except:
            title = url
        #get the logo's URL
        try:
            icon = favicon.get(url)[0].url
        except:
            icon = "https://cdn-icons-png.flaticon.com/128/1006/1006771.png"
        #Save data in database
        new_password = Password.objects.create(
            user=request.user,
            name=title,
            logo=icon,
            url=encrypted_url,
            username=encrypted_username,
            password=encrypted_password.decode(),
        )
        msg = f"{title} created successfully."
        messages.success(request, msg)
        return redirect('home')

    context = {'form': form, 'password': password}            
    return render(request, 'base/create_password.html', context)


@login_required(login_url='/login/')
def password_details(request, pk):
    passwords = Password.objects.filter(id=pk)
    context = {'passwords': passwords}

    if request.user.is_authenticated:
        passwords = Password.objects.filter(id=pk).filter(user=request.user)
        for password in passwords:
            password.password = fernet.encrypt(password.password.encode()).decode()
        context = {'passwords':passwords}

    return render(request, 'base/password_details.html', context)


@login_required(login_url='login')
def update_password(request, pk):
    password = Password.objects.get(id=pk)

    if request.method == 'POST':
        form = PasswordForm(data=request.POST, instance=password)
        url = request.POST.get("url")
        password = request.POST.get("password")
        #ecrypt data
        encrypted_url = url
        encrypted_password = fernet.encrypt(password.encode()).decode()
        #get title of the website
        try:
            br.open(url)
            title = br.title()
        except:
            title = url
        #get the logo's URL
        try:
            icon = favicon.get(url)[0].url
        except:
            icon = "https://cdn-icons-png.flaticon.com/128/1006/1006771.png"

        if form.is_valid():
            password = form.save(commit=False)
            password.url = encrypted_url
            password.logo = icon
            password.name = title
            password.password = encrypted_password
            msg = f"{title} Updated successfully."
            password.save()
            messages.success(request, msg)
            return redirect('home')

    else:
        form = PasswordForm()

    context = {}
    if request.user.is_authenticated:
        passwords = Password.objects.filter(id=pk).filter(user=request.user)
        for password in passwords:
            password.password = fernet.decrypt(password.password.encode()).decode()
    
    context = {'password': password}
    return render(request, 'base/create_password.html', context)


@login_required(login_url='login')
def delete_password(request, pk):
    password = Password.objects.get(id=pk)

    if request.user != password.user:
        return HttpResponse('You are not allowed to do that!')

    if request.method == 'POST':
        password.delete()
        msg = f"{password.name} deleted successfully."
        messages.success(request, msg)
        return redirect('home')

    context = {'password': password}
    return render(request, 'base/delete.html', context)
