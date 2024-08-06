from django.urls import path
from . import views


urlpatterns = [
    path('', views.main, name='main'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/', views.view_task, name='view_task'),
    path('tasks/<int:task_id>/update/', views.update_task, name='update_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('tasks/grant_permission/<int:task_id>/<int:user_id>/<str:permission_type>/', views.grant_permission, name='grant_permission'),
    path('tasks/revoke_permission/<int:task_id>/<int:user_id>/<str:permission_type>/', views.revoke_permission, name='revoke_permission'),
]
