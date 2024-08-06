from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Task, TaskPermission

User = get_user_model()


class TaskTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user', password='password')
        self.client.login(username='user', password='password')
        self.task = Task.objects.create(title='Test Task', description='Test Description', author=self.user)

    def test_create_task(self):
        response = self.client.post(reverse('create_task'), {
            'title': 'New Task',
            'description': 'New Description'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Task "New Task" created successfully!', response.content.decode())
        self.assertTrue(Task.objects.filter(title='New Task').exists())

    def test_list_tasks(self):
        response = self.client.get(reverse('list_tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Task', response.content.decode())

    def test_update_task(self):
        response = self.client.post(reverse('update_task', args=[self.task.id]), {
            'title': 'Updated Task',
            'description': 'Updated Description'
        })
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')

    def test_delete_task(self):
        response = self.client.post(reverse('delete_task', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_assign_permission(self):
        user2 = User.objects.create_user(username='user2', password='password2')
        response = self.client.post(reverse('grant_permission', args=[self.task.id, user2.id]), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(TaskPermission.objects.filter(task=self.task, user=user2, permission_update=True).exists())

    def test_remove_permission(self):
        user2 = User.objects.create_user(username='user2', password='password2')
        TaskPermission.objects.create(task=self.task, user=user2, permission_update=True)
        response = self.client.post(reverse('revoke_permission', args=[self.task.id, user2.id]), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TaskPermission.objects.filter(task=self.task, user=user2, permission_update=True).exists())
