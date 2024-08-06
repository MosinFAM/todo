from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return f'{self.title}'


class TaskPermission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_permission = models.BooleanField(default=False)
    update_permission = models.BooleanField(default=False)

    class Meta:
        unique_together = ('task', 'user')

    def __str__(self):
        permissions = []
        if self.read_permission:
            permissions.append("Read")
        if self.update_permission:
            permissions.append("Update")
        return f"{self.user.username} - {self.task.title} - {', '.join(permissions)}"
