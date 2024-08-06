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
    READ = 'read'
    UPDATE = 'update'

    PERMISSION_CHOICES = [
        (READ, 'Read'),
        (UPDATE, 'Update'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission_update = models.BooleanField(default=False)

    class Meta:
        unique_together = ('task', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.task.title} - {'Can update' if self.can_update else 'Cannot update'}"
