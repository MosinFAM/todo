from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task, TaskPermission
from .forms import TaskForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt


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
        permission = TaskPermission.objects.filter(task=task, user=request.user, update_permission=True).exists()
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
    if task.author != request.user:
        permission = TaskPermission.objects.filter(task=task, user=request.user, read_permission=True).exists()
        if not permission:
            return HttpResponseForbidden("You don't have permission to view this task.")

    return HttpResponse(f'Task: {task.title}, Description: {task.description}')


# @csrf_exempt
# @login_required
def main(request):
    return HttpResponse("ToDo")


@csrf_exempt
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, author=request.user)
    if request.method == 'POST':
        if request.user == task.author:
            task.delete()
            return HttpResponse(f'Task "{task.title}" deleted successfully!')
        return HttpResponseForbidden("You don't have permission to delete this task.")
    return HttpResponseNotAllowed(['POST'])


@csrf_exempt
@login_required
def grant_permission(request, task_id, user_id, permission_type):
    task = get_object_or_404(Task, id=task_id, author=request.user)
    other_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        permission, created = TaskPermission.objects.get_or_create(
            task=task, user=other_user
        )

        if permission_type == 'read':
            permission.read_permission = True
            permission.save()
            return HttpResponse(f'Permission "read" granted to {other_user.username} for task "{task.title}".')
        elif permission_type == 'update':
            permission.read_permission = True
            permission.update_permission = True
            permission.save()
            return HttpResponse(f'Permission "update" granted to {other_user.username} for task "{task.title}".')
        else:
            return HttpResponse('Invalid permission type.')

    return HttpResponseNotAllowed(['POST'])


@csrf_exempt
@login_required
def revoke_permission(request, task_id, user_id, permission_type):
    task = get_object_or_404(Task, id=task_id, author=request.user)
    other_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        try:
            permission = TaskPermission.objects.get(task=task, user=other_user)

            if permission_type == 'read':
                permission.read_permission = False
                permission.update_permission = False
                permission.save()
                return HttpResponse(f'Permission "read" revoked from {other_user.username} for task "{task.title}".')
            elif permission_type == 'update':
                permission.update_permission = False
                permission.save()
                return HttpResponse(f'Permission "update" revoked from {other_user.username} for task "{task.title}".')
            else:
                return HttpResponse('Invalid permission type.')

        except TaskPermission.DoesNotExist:
            return HttpResponse(f'Permission does not exist for {other_user.username}.')

    return HttpResponseNotAllowed(['POST'])
