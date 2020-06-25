from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login


def signup_user(request):
    if request.method == 'GET':
        return render(request, '../templates/todo_app/signup_user.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('current_todos')
            except IntegrityError:
                return render(request,
                              '../templates/todo_app/signup_user.html',
                              {'form': UserCreationForm(),
                               'error': "This username is already taken. Please, choose another one."}
                              )
        else:
            return render(request, '../templates/todo_app/signup_user.html',
                          {'form': UserCreationForm(), 'error': "Passwords didn't match"})


def current_todos(request):
    return render(request, '../templates/todo_app/current_todos.html', {'form': UserCreationForm()})