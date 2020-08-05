from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm, GroupForm
from .models import Todo, Group, GroupUser
from django.utils import timezone
from django.contrib.auth.decorators import login_required


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


@login_required
def current_todos(request):
    todos = Todo.objects.filter(user=request.user, completion_time__isnull=True).order_by('-creation_time')
    return render(request, '../templates/todo_app/current_todos.html', {'todos': todos})


@login_required
def completed_todos(request):
    todos = Todo.objects.filter(user=request.user, completion_time__isnull=False).order_by('-completion_time')
    return render(request, '../templates/todo_app/completed_todos.html', {'todos': todos})


@login_required
def view_todo(request, todo_pk):
    todo_obj = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo_obj)
        return render(request, '../templates/todo_app/view_todo.html', {'todo': todo_obj, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo_obj)
            form.save()
            return redirect('current_todos')
        except ValueError:
            return render(request, '../templates/todo_app/view_todo.html',
                          {'todo': todo_obj, 'form': form, 'error': 'Bad data. Fuck you!'})


@login_required
def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def home(request):
    return render(request, 'todo_app/home.html')


def login_user(request):
    if request.method == 'GET':
        return render(request, '../templates/todo_app/login_user.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, '../templates/todo_app/login_user.html',
                          {'form': AuthenticationForm(), 'error': "Username and/or password didn't match"})
        else:
            login(request, user)
            return redirect('current_todos')


@login_required
def create_todo(request):
    if request.method == 'GET':
        return render(request, '../templates/todo_app/create_todo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            new_todo = form.save(commit=False)
            new_todo.user = request.user
            new_todo.save()
            return redirect('current_todos')
        except ValueError:
            return render(request, '../templates/todo_app/create_todo.html',
                          {'form': TodoForm(), 'error': 'Bad data. Fuck you.'})


@login_required
def complete_todo(request, todo_pk):
    if request.method == 'POST':
        todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
        todo.completion_time = timezone.now()
        todo.save()
        return redirect('current_todos')


@login_required
def delete_todo(request, todo_pk):
    if request.method == 'POST':
        todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
        todo.delete()
        return redirect('current_todos')


@login_required
def groups(request):
    _groups = [membership.group for membership in GroupUser.objects.filter(user=request.user)
               if membership.status != 'I']
    return render(request, '../templates/todo_app/groups.html', {'groups': _groups})


@login_required
def create_group(request):
    if request.method == 'GET':
        return render(request, '../templates/todo_app/create_group.html', {'form': GroupForm})
    else:
        _group = Group.objects.create(name=request.POST['name'])
        _group.users.add(request.user, through_defaults={'status': 'C'})
        _group.save()
        return redirect('groups')


@login_required
def group(request, group_id):
    membership = get_object_or_404(GroupUser, group=group_id, user=request.user)
    members = [member.user for member in GroupUser.objects.filter(group=group_id) if member.status != 'I']
    if membership.status == 'I':
        return HttpResponse(404)
    if request.method == 'GET':
        _group = Group.objects.get(pk=group_id)
        return render(request, '../templates/todo_app/group.html',
                      {'group': _group, 'status': membership.status, 'members': members})
    else:
        if 'username' in request.POST:
            if not User.objects.filter(username=request.POST['username']).exists():
                try:
                    GroupUser.objects.create(group=get_object_or_404(Group, pk=group_id),
                                             user=User.objects.get(username=request.POST['username']),
                                             status='I').save()
                    return redirect('groups')
                except User.DoesNotExist:
                    _group = Group.objects.get(pk=group_id)
                    return render(request, '../templates/todo_app/group.html',
                                  {'group': _group, 'error': 'User does not exist',
                                   'status': membership.status, 'members': members})
            else:
                _group = Group.objects.get(pk=group_id)
                return render(request, '../templates/todo_app/group.html',
                              {'group': _group, 'error': 'Invite has already been sent',
                               'status': membership.status, 'members': members})
        else:
            get_object_or_404(Group, pk=group_id).delete()
            return redirect('groups')
