from django.shortcuts import render

# Create your views here.



from django.shortcuts import render
from django.contrib.auth.decorators import login_required




from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)

                # Redirect based on role
                if user.role == 'superadmin' or user.role == 'admin':
                    return redirect('admin_panel')
                else:
                    return redirect('user_tasks')
            else:
                messages.error(request, 'Account disabled.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'tasks/login.html')

from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.shortcuts import render, redirect

User = get_user_model()

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST.get('role', 'user')  # default to 'user'

        if User.objects.filter(username=username).exists():
            return render(request, 'tasks/register.html', {'error': 'Username already exists'})

        user = User.objects.create_user(username=username, password=password, role=role)
        login(request, user)
        return redirect('admin_panel')
    
    return render(request, 'tasks/register.html')


from django.contrib.auth import logout

def custom_logout(request):
    logout(request)
    return redirect('login')







from rest_framework import viewsets, permissions
from .models import CustomUser, Task, TaskReport, AdminUserAssignment
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import action

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin]

class AdminUserAssignmentViewSet(viewsets.ModelViewSet):
    queryset = AdminUserAssignment.objects.all()
    serializer_class = AdminUserAssignmentSerializer
    permission_classes = [IsSuperAdmin]

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Task.objects.all()
        elif user.role == 'admin':
            assigned_users = AdminUserAssignment.objects.filter(admin=user).values_list('user', flat=True)
            return Task.objects.filter(assigned_to__in=assigned_users)
        return Task.objects.none()

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

class TaskReportViewSet(viewsets.ModelViewSet):
    serializer_class = TaskReportSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return TaskReport.objects.all()
        elif user.role == 'admin':
            users = AdminUserAssignment.objects.filter(admin=user).values_list('user', flat=True)
            return TaskReport.objects.filter(user__in=users)
        elif user.role == 'user':
            return TaskReport.objects.filter(user=user)
        return TaskReport.objects.none()

    def get_permissions(self):
        return [permissions.IsAuthenticated()]


from django.contrib.auth.decorators import login_required, user_passes_test

def superadmin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'superadmin')(view_func)

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'admin')(view_func)

def user_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'user')(view_func)

# tasks/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Task, CustomUser
from .forms import TaskForm, CompletionReportForm

def superadmin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'superadmin')(view_func)

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'admin')(view_func)

def user_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'user')(view_func)

# @login_required
# def admin_panel(request):
#     user = request.user
#     if user.role == 'superadmin':
#         tasks = Task.objects.all()
#         users = CustomUser.objects.all()
#     elif user.role == 'admin':
#         tasks = Task.objects.filter(assigned_to__role='user')
#         users = CustomUser.objects.filter(role='user')
#     else:
#         return redirect('user_tasks')

#     form = TaskForm()

#     context = {
#         'tasks': tasks,
#         'users': users,
#         'form': form,
#         'role': user.role,
#     }
#     return render(request, 'tasks/admin_panel.html', context)
@login_required
def admin_panel(request):
    user = request.user
    editing_task_id = request.GET.get('edit')

    if user.role == 'superadmin':
        tasks = Task.objects.all()
        users = CustomUser.objects.all()
    elif user.role == 'admin':
        tasks = Task.objects.all()
        users = CustomUser.objects.all()
        # Apply admin filtering logic here if needed
    else:
        return redirect('user_tasks')

    form = TaskForm()
    if user.role == 'admin':
        form.fields['assigned_to'].queryset = users

    context = {
        'tasks': tasks,
        'users': users,
        'form': form,
        'role': user.role,
        'editing_task_id': int(editing_task_id) if editing_task_id else None,
        'status_choices': Task.STATUS_CHOICES,
    }
    return render(request, 'tasks/admin_panel.html', context)



@login_required
@user_required
def user_tasks(request):
    user = request.user
    tasks = Task.objects.filter(assigned_to=user)

    context = {
        'tasks': tasks,
    }
    return render(request, 'tasks/user_tasks.html', context)

@login_required
@user_required
def submit_report(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)

    if request.method == 'POST':
        form = CompletionReportForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            task.status = 'completed'  # Automatically mark completed
            task.save()
            return redirect('user_tasks')
    else:
        form = CompletionReportForm(instance=task)

    return render(request, 'tasks/submit_report.html', {'form': form, 'task': task})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Task
from .forms import TaskForm, CompletionReportForm

# Check if user is admin or superuser
def is_admin(user):
    return user.is_staff or user.is_superuser



def is_admin_or_superadmin(user):
    return user.is_authenticated and (user.role == 'admin' or user.role == 'superadmin')




# #new..........
# @login_required
# def task_create(request):
#     if request.method == 'POST':
#         form = TaskForm(request.POST)
#         if form.is_valid():
#             task = form.save(commit=False)
#             task.assigned_by = request.user
#             task.save()
#             return redirect('admin_panel')
#     else:
#         form = TaskForm()
#     return render(request, 'tasks/task_form.html', {'form': form})
@login_required
@user_passes_test(is_admin_or_superadmin)
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        form.fields['assigned_to'].queryset = CustomUser.objects.filter(role='user')
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            print("✅ Task saved:", task.title)
            return redirect('admin_panel')
        else:
            print("❌ Form errors:", form.errors)
    else:
        form = TaskForm()
        form.fields['assigned_to'].queryset = CustomUser.objects.filter(role='user')
    return render(request, 'tasks/task_form.html', {'form': form})














@login_required
@user_required
def user_tasks(request):
    user = request.user
    tasks = Task.objects.filter(assigned_to=user)

    context = {
        'tasks': tasks,
    }
    return render(request, 'tasks/user_tasks.html', context)


@login_required
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
    if request.method == 'POST':
        form = CompletionReportForm(request.POST, instance=task)
        if form.is_valid():
            # Mark task completed on submit
            task.status = 'Completed'
            form.save()
            return redirect('user_tasks')
    else:
        form = CompletionReportForm(instance=task)
    return render(request, 'tasks/task_complete.html', {'form': form, 'task': task})

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('admin_panel') 
        else:
            return render(request, 'tasks/login.html', {'error': 'Invalid credentials'})
    return render(request, 'tasks/login.html')



from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def home_redirect(request):
    user = request.user
    if user.role == 'superadmin' or user.role == 'admin':
        return redirect('admin_panel')
    else:
        return redirect('user_tasks')




@login_required
@user_passes_test(is_admin_or_superadmin)
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    user = request.user
    if user.role == 'admin':
        assigned_users_ids = AdminUserAssignment.objects.filter(admin=user).values_list('user', flat=True)
        if task.assigned_to.id not in assigned_users_ids:
            return redirect('admin_panel')  # or 403 Forbidden
    form = TaskForm(request.POST or None, instance=task)
    if form.is_valid():
        form.save()
        return redirect('admin_panel')
    return render(request, 'tasks/task_form.html', {'form': form})



from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Task

@login_required
def delete_task(request, task_id):
    if request.user.role != 'superadmin':
        return HttpResponseForbidden("You are not authorized to delete tasks.")

    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        task.delete()
        return redirect('admin_panel')  # Change this to the correct name of your admin panel URL

    return HttpResponseForbidden("Invalid request method.")

@login_required
def task_update_inline(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        task.due_date = request.POST.get('due_date')
        task.status = request.POST.get('status')
        task.completion_report = request.POST.get('completion_report')

        # Handle worked_hours safely
        worked_hours = request.POST.get('worked_hours')
        task.worked_hours = float(worked_hours) if worked_hours else None

        # Handle assigned_to safely
        assigned_to_id = request.POST.get('assigned_to')
        if assigned_to_id:
            task.assigned_to = get_object_or_404(CustomUser, id=assigned_to_id)

        task.save()

    return redirect('admin_panel')



from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import CustomUser

@login_required
def promote_to_admin(request, user_id):
    if request.user.role != 'superadmin':
        return redirect('admin_panel')  # or raise PermissionDenied

    user = get_object_or_404(CustomUser, id=user_id)
    user.role = 'admin'
    user.save()
    return redirect('admin_panel')


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import CustomUser

@login_required
def downgrade_to_user(request, user_id):
    if request.user.role != 'superadmin':
        return redirect('admin_panel')  # or raise PermissionDenied

    user = get_object_or_404(CustomUser, id=user_id)
    if user.role == 'admin':  # Only downgrade admins
        user.role = 'user'
        user.save()
    return redirect('admin_panel')





#new
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

@login_required
def delete_user(request, user_id):
    if request.user.role != 'superadmin':
        messages.error(request, "You do not have permission to delete users.")
        return redirect('admin_panel')

    user_to_delete = get_object_or_404(CustomUser, id=user_id)

    if user_to_delete == request.user:
        messages.error(request, "You cannot delete yourself.")
        return redirect('admin_panel')

    user_to_delete.delete()
    messages.success(request, f"User {user_to_delete.username} has been deleted.")
    return redirect('admin_panel')
