from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User, through='GroupUser')

    def __str__(self):
        return self.name


class Todo(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    importance = models.BooleanField(default=False)
    creation_time = models.DateTimeField(auto_now_add=True)
    completion_time = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.title


class GroupUser(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    STATUS_TYPES = (
        ('C', 'Creator'),
        ('M', 'Member'),
        ('I', 'Invited')
    )
    status = models.CharField(max_length=1, choices=STATUS_TYPES)
