from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import logout


# Create your views here.

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Login successful')
            return redirect('home')

    else :
        messages.error(request, 'INVALIDE AUTHENTIFICATION, try again')
    return render(request, 'accounts/login.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, 'password is incorrect')
            return redirect('register')
        else:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'that username is taken')
                return redirect('register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'that email is being used')
                    return redirect('register')
                else:
                    user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                    )
                    user.set_password(password)
                    user.gender = gender

                    user.save()
                    messages.success(request, 'you are now register can login')
                    return redirect('login')

    else:
        return render(request, 'accounts/register.html')

def logout_view(request):
    logout(request)
    return redirect ('login')