from django.forms import ModelForm
from .models import Todo, Group


class TodoForm(ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'importance', 'group']


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ['name', ]