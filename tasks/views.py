from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task, TaskPermission
from .forms import TaskForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def list_tasks(request):
    tasks = Task.objects.all().order_by('-created_at')
    tasks_data = [
        {
            'title': task.title,
        }
        for task in tasks
    ]
    return JsonResponse({'tasks': tasks_data})


@csrf_exempt
@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.author = request.user
            task.save()
            return HttpResponse(f'Task "{task.title}" created successfully!')
        else:
            return HttpResponse('Error creating task: ' + str(form.errors))
    return HttpResponseNotAllowed(['POST'])


@csrf_exempt
@login_required
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.author != request.user:
        permission = TaskPermission.objects.filter(task=task, user=request.user, permission_update=True).exists()
        if not permission:
            return HttpResponseForbidden("You don't have permission to update this task.")

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return HttpResponse(f'Task "{task.title}" updated successfully!')
        else:
            return HttpResponse('Error updating task: ' + str(form.errors))
    return HttpResponseNotAllowed(['POST'])


@csrf_exempt
@login_required
def view_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    return HttpResponse(f'Task: {task.title}, Description: {task.description}')


# @csrf_exempt
# @login_required
def main(request):

    return HttpResponse("ToDo")


@csrf_exempt
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, author=request.user)
    if request.method == 'POST' and request.user == task.author:
        task.delete()
        return HttpResponse(f'Task "{task.title}" deleted successfully!')
    return HttpResponseNotAllowed(['POST'])


@csrf_exempt
@login_required
def grant_permission(request, task_id, user_id):
    task = get_object_or_404(Task, id=task_id, author=request.user)
    other_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        permission, created = TaskPermission.objects.get_or_create(
            task=task, user=other_user,
            defaults={'permission_update': True}
        )
        if created:
            return HttpResponse(f'Permission "update" granted to {other_user.username} for task "{task.title}".')
        else:
            permission.permission_update = True
            permission.save()
            return HttpResponse(f'Permission "update" already exists for {other_user.username}.')

    return HttpResponseNotAllowed(['POST'])


@csrf_exempt
@login_required
def revoke_permission(request, task_id, user_id):
    task = get_object_or_404(Task, id=task_id, author=request.user)
    other_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        try:
            permission = TaskPermission.objects.get(task=task, user=other_user)
            if permission.permission_update:
                permission.permission_update = False
                permission.save()
                return HttpResponse(f'Permission "update" revoked from {other_user.username} for task "{task.title}".')
            else:
                return HttpResponse(f'Permission "update" does not exist for {other_user.username}.')
        except TaskPermission.DoesNotExist:
            return HttpResponse(f'Permission does not exist for {other_user.username}.')
    
    return HttpResponseNotAllowed(['POST'])
