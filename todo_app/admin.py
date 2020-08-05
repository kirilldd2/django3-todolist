from django.contrib import admin
from .models import Todo, Group, GroupUser


class TodoAdmin(admin.ModelAdmin):
    readonly_fields = ('creation_time', )


admin.site.register(Todo, TodoAdmin)
admin.site.register(Group)
admin.site.register(GroupUser)
