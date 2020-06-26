from django.db import models
from django.contrib.auth.models import User


class Todo(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    importance = models.BooleanField(default=False)
    creation_time = models.DateTimeField(auto_now_add=True)
    completion_time = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
