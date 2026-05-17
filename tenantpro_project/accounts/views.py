from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import User

def login_view(request):
    if request.user.is_authenticated:
        return _redirect_role(request.user)
    if request.method == 'POST':
        username = request.POST.get('username','').strip()
        password = request.POST.get('password','')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return _redirect_role(user)
        messages.error(request, 'Invalid credentials.')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

def register_view(request):
    if request.user.is_authenticated:
        return _redirect_role(request.user)
    if request.method == 'POST':
        role = request.POST.get('role','tenant')
        # Prevent registering as admin via form
        if role not in ['tenant', 'owner', 'society_admin']:
            role = 'tenant'
        uname = request.POST.get('username','').strip()
        email = request.POST.get('email','').strip()
        pwd   = request.POST.get('password','')
        fname = request.POST.get('first_name','').strip()
        lname = request.POST.get('last_name','').strip()
        phone = request.POST.get('phone','').strip()
        if User.objects.filter(username=uname).exists():
            messages.error(request, 'Username already taken.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            u = User.objects.create_user(username=uname, email=email, password=pwd,
                first_name=fname, last_name=lname, phone=phone, role=role)
            login(request, u)
            messages.success(request, f'Welcome, {fname}!')
            return _redirect_role(u)
    return render(request, 'accounts/register.html')

def _redirect_role(user):
    # Fix 3: society_admin now has proper redirect
    role_map = {
        'admin': '/admin-zone/',
        'owner': '/owner/',
        'society_admin': '/society-admin/',
        'tenant': '/tenant/',
    }
    if user.is_staff or user.is_superuser:
        return redirect('/admin-zone/')
    return redirect(role_map.get(user.role, '/tenant/'))
