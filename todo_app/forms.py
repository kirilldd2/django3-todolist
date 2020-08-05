from django.forms import ModelForm
from .models import Todo, Group


class TodoForm(ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'importance']


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ['name', ]