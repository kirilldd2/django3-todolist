"""todolist URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from todo_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),

    # Auth

    path('signup/', views.signup_user, name='signup_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('login/', views.login_user, name='login_user'),

    # Todolist

    path('current/', views.current_todos, name='current_todos'),
    path('completed/', views.completed_todos, name='completed_todos'),
    path('create/', views.create_todo, name='create_todo'),
    path('todo/<int:todo_pk>/edit/', views.edit_todo, name='edit_todo'),
    path('todo/<int:todo_pk>/complete/', views.complete_todo, name='complete_todo'),
    path('todo/<int:todo_pk>/delete/', views.delete_todo, name='delete_todo'),
    path('todo/<int:todo_pk>/', views.view_todo, name='view_todo'),


    # Groups

    path('groups/', views.groups, name='groups'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/<int:group_id>/', views.group, name='group'),
    path('groups/accept/', views.group_accept, name='group_accept'),
]
