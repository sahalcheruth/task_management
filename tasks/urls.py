
from django.urls import path

from . import views


urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/tasks/create/', views.task_create, name='task_create'),
    path('admin-panel/tasks/<int:pk>/edit/', views.task_update, name='task_update'),
    
    path('login/', views.custom_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout, name='logout'),
    path('user-tasks/', views.user_tasks, name='user_tasks'),
    path('submit-report/<int:task_id>/', views.submit_report, name='submit_report'),
    path('tasks/', views.user_tasks, name='user_tasks'),
    path('tasks/<int:pk>/complete/', views.task_complete, name='task_complete'),
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('tasks/<int:pk>/update-inline/', views.task_update_inline, name='task_update_inline'),
    path('promote/<int:user_id>/', views.promote_to_admin, name='promote_to_admin'),
    path('downgrade/<int:user_id>/', views.downgrade_to_user, name='downgrade_to_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('manage-users/', views.manage, name='manage-users'),
   
]


