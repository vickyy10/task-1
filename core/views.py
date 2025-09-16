from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import User, Task
from .forms import UserForm, TaskForm
from .utils import *


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                # Redirect based on role
                if user.is_superadmin:
                    return redirect("superadmin_dashboard")
                elif user.is_admin:
                    return redirect("admin_dashboard")
                else:
                    return redirect("user_dashboard")
            else:
                messages.error(request, "Your account is inactive.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")  


@login_required
def dashboard(request):
    if request.user.is_superadmin:
        return superadmin_dashboard(request)
    elif request.user.is_admin:
        return admin_dashboard(request)
    else:
        return redirect('user_dashboard')  
    
from django.contrib.auth import authenticate, login,logout



@superadmin_required
def superadmin_dashboard(request):
    user_count = User.objects.filter(role='user').count()
    admin_count = User.objects.filter(role='admin').count()
    task_count = Task.objects.count()
    pending_tasks = Task.objects.filter(status='pending').count()
    recent_tasks = Task.objects.all().order_by('-created_at')[:5]
    recent_users = User.objects.all().order_by('-date_joined')[:5]
    
    context = {
        'user_count': user_count,
        'admin_count': admin_count,
        'task_count': task_count,
        'pending_tasks': pending_tasks,
        'recent_tasks': recent_tasks,
        'recent_users': recent_users,
    }
    
    return render(request, 'superadmin_dashboard.html', context)

@admin_required
def admin_dashboard(request):
    assigned_users = User.objects.filter(assigned_admin=request.user, role='user')
    assigned_users_count = assigned_users.count()
    user_tasks = Task.objects.filter(assigned_to__in=assigned_users)
    user_task_count = user_tasks.count()
    pending_user_tasks = user_tasks.filter(status='pending').count()
    completed_user_tasks = user_tasks.filter(status='completed').count()
    recent_tasks = user_tasks.order_by('-created_at')[:5]
    
    context = {
        'assigned_users': assigned_users[:5],
        'assigned_users_count': assigned_users_count,
        'user_task_count': user_task_count,
        'pending_user_tasks': pending_user_tasks,
        'completed_user_tasks': completed_user_tasks,
        'recent_tasks': recent_tasks,
    }
    
    return render(request, 'admin_dashboard.html', context)

@login_required
def user_dashboard(request):
    if request.user.is_superadmin or request.user.is_admin:
        return redirect('dashboard')
    tasks = Task.objects.filter(assigned_to=request.user)
    pending_tasks = tasks.filter(status='pending')
    in_progress_tasks = tasks.filter(status='in_progress')
    completed_tasks = tasks.filter(status='completed') 
    recent_tasks = tasks.order_by('-created_at')[:5]
    
    context = {
        'pending_tasks_count': pending_tasks.count(),
        'in_progress_tasks_count': in_progress_tasks.count(),
        'completed_tasks_count': completed_tasks.count(),
        'total_tasks': tasks.count(),
        'recent_tasks': recent_tasks,
    }
    
    return render(request, 'dashboard.html', context)



@superadmin_required
def user_list(request):
    users = User.objects.filter(role='user',is_superuser=False).order_by('-date_joined')
    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)
    
    page = request.GET.get('page', 1)
    paginator = Paginator(users, 10) 
    
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    context = {
        'users': users,
    }
    
    return render(request, 'user_list.html', context)



@login_required
def user_detail(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    assigned_tasks = Task.objects.filter(assigned_to=user_obj).order_by('-created_at')
    
    context = {
        'user_obj': user_obj,
        'assigned_tasks': assigned_tasks
    }
    return render(request, 'user_detail.html', context)



@superadmin_required
def admin_list(request):
    admins = User.objects.filter(role='admin').order_by('-date_joined')

    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'active':
            admins = admins.filter(is_active=True)
        elif status_filter == 'inactive':
            admins = admins.filter(is_active=False)
    
    page = request.GET.get('page', 1)
    paginator = Paginator(admins, 10)
    
    try:
        admins = paginator.page(page)
    except PageNotAnInteger:
        admins = paginator.page(1)
    except EmptyPage:
        admins = paginator.page(paginator.num_pages)
    
    context = {
        'admins': admins,
    }
    
    return render(request, 'admin_list.html', context)



@login_required
def user_task_list(request):
    if request.user.is_superadmin or request.user.is_admin:
        return redirect('dashboard')
    
    tasks = Task.objects.filter(assigned_to=request.user)
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    tasks = tasks.order_by('-created_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(tasks, 10)  
    
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)
    
    context = {
        'tasks': tasks,
    }
    
    return render(request, 'user/task_list.html', context)



@login_required
def user_task_detail(request, task_id):
    if request.user.is_superadmin or request.user.is_admin:
        return redirect('dashboard')
    
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    
    context = {
        'task': task,
    }
    
    return render(request, 'user/task_detail.html', context)



@login_required
def user_start_task(request, task_id):
    if request.user.is_superadmin or request.user.is_admin:
        return redirect('dashboard')
    
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    
    if task.status == 'pending':
        task.status = 'in_progress'
        task.started_at = timezone.now()
        task.save()
        messages.success(request, f'Task "{task.title}" has been started.')
    else:
        messages.warning(request, f'Task "{task.title}" cannot be started.')
    
    return redirect('user_task_detail', task_id=task.id)



@login_required
def user_complete_task(request, task_id):
    if request.user.is_superadmin or request.user.is_admin:
        return redirect('dashboard')
    
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    
    if request.method == 'POST':
        completion_report = request.POST.get('completion_report', '')
        worked_hours = request.POST.get('worked_hours', 0)
        
        try:
            worked_hours = float(worked_hours)
            if worked_hours <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, 'Please enter a valid number of hours worked.')
            return redirect('user_task_detail', task_id=task.id)
        
        if not completion_report:
            messages.error(request, 'Completion report is required.')
            return redirect('user_task_detail', task_id=task.id)
        
        task.status = 'completed'
        task.completion_report = completion_report
        task.worked_hours = worked_hours
        task.completed_at = timezone.now()
        task.save()
        
        messages.success(request, f'Task "{task.title}" has been completed successfully.')
        return redirect('user_task_list')
    
    context = {
        'task': task,
    }
    
    return render(request, 'user/complete_task.html', context)



@superadmin_required
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            
            user.save()
            messages.success(request, f'User {user.username} created successfully.')
            return redirect('user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'user_form.html', context)



@superadmin_required
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)   
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            
            user.save()
            messages.success(request, f'User {user.username} updated successfully.')
            return redirect('user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
    }
    
    return render(request, 'user_form.html', context)



@superadmin_required
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully.')
        return redirect('user_list')
    
    context = {
        'user': user,
    }
    
    return render(request, 'user_confirm_delete.html', context)



@superadmin_required
def user_toggle_active(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if user != request.user: 
        user.is_active = not user.is_active
        user.save()
        
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f'User {user.username} {status} successfully.')
    return redirect('user_list')


@superadmin_required
def admin_toggle_active(request, user_id):
    user = get_object_or_404(User, id=user_id)
    print(user,'lllllllllllllllllllllllllllllllll')
    if user != request.user: 
        user.is_active = not user.is_active
        user.save()
        print(user.is_active,'hhhhhhhhhhhhhhhhhhhhhhhhhh')
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f'admin {user.username} {status} successfully.')
    return redirect('admin_list')



@login_required
def task_list(request):
    if request.user.is_superadmin:
        tasks = Task.objects.all()
    elif request.user.is_admin:
        assigned_users = User.objects.filter(assigned_admin=request.user, role='user')
        tasks = Task.objects.filter(assigned_to__in=assigned_users)
    else:  
        tasks = Task.objects.filter(assigned_to=request.user)

    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    assigned_to_filter = request.GET.get('assigned_to')
    if assigned_to_filter:
        tasks = tasks.filter(assigned_to_id=assigned_to_filter)
    
    due_date_filter = request.GET.get('due_date')
    if due_date_filter:
        try:
            due_date = datetime.strptime(due_date_filter, '%Y-%m-%d').date()
            tasks = tasks.filter(due_date__date=due_date)
        except ValueError:
            pass
    
    tasks = tasks.order_by('-created_at')
    
    page = request.GET.get('page', 1)
    paginator = Paginator(tasks, 10)
    
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)
    
    context = {
        'tasks': tasks,
    }
    
    return render(request, 'task_list.html', context)



@superadmin_or_admin_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" created successfully.')
            return redirect('task_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm(user=request.user)
    
    context = {
        'form': form,
    }
    
    return render(request, 'task_form.html', context)



@superadmin_or_admin_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if not request.user.is_superadmin and task.assigned_to.assigned_admin != request.user:
        messages.error(request, 'You do not have permission to edit this task.')
        return redirect('task_list')
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            task = form.save()
            messages.success(request, f'Task "{task.title}" updated successfully.')
            return redirect('task_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm(instance=task, user=request.user)
    
    context = {
        'form': form,
        'task': task,
    }
    
    return render(request, 'task_form.html', context)



@superadmin_or_admin_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if not request.user.is_superadmin and task.assigned_to.assigned_admin != request.user:
        messages.error(request, 'You do not have permission to delete this task.')
        return redirect('task_list')
    
    if request.method == 'POST':
        title = task.title
        task.delete()
        messages.success(request, f'Task "{title}" deleted successfully.')
        return redirect('task_list')
    
    context = {
        'task': task,
    }
    
    return render(request, 'task_confirm_delete.html', context)



@superadmin_or_admin_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if not request.user.is_superadmin and task.assigned_to.assigned_admin != request.user:
        messages.error(request, 'You do not have permission to view this task.')
        return redirect('task_list')
    
    context = {
        'task': task,
    }
    
    return render(request, 'task_detail.html', context)



@superadmin_or_admin_required
def reports(request):
    if request.user.is_superadmin:
        tasks = Task.objects.filter(status='completed')
        report_users = User.objects.filter(role='user')
    else: 
        assigned_users = User.objects.filter(assigned_admin=request.user, role='user')
        tasks = Task.objects.filter(assigned_to__in=assigned_users, status='completed')
        print()
        report_users = assigned_users
    
    user_filter = request.GET.get('user')
    if user_filter:
        tasks = tasks.filter(assigned_to_id=user_filter)
    
    date_from_filter = request.GET.get('date_from')
    if date_from_filter:
        try:
            date_from = datetime.strptime(date_from_filter, '%Y-%m-%d').date()
            tasks = tasks.filter(due_date__date__gte=date_from)
        except ValueError:
            pass
    
    date_to_filter = request.GET.get('date_to')
    if date_to_filter:
        try:
            date_to = datetime.strptime(date_to_filter, '%Y-%m-%d').date()
            tasks = tasks.filter(due_date__date__lte=date_to)
        except ValueError:
            pass
    
    total_completed_tasks = tasks.count()
    total_worked_hours = tasks.aggregate(Sum('worked_hours'))['worked_hours__sum'] or 0
    avg_hours_per_task = tasks.aggregate(Avg('worked_hours'))['worked_hours__avg'] or 0
    
    tasks = tasks.order_by('-due_date')
    
    page = request.GET.get('page', 1)
    paginator = Paginator(tasks, 10) 
    
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)
    
    context = {
        'tasks': tasks,
        'report_users': report_users,
        'total_completed_tasks': total_completed_tasks,
        'total_worked_hours': total_worked_hours,
        'avg_hours_per_task': avg_hours_per_task,
    }
    
    return render(request, 'reports.html', context)




@login_required
def update_task_status(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        status = request.POST.get('status')
        worked_hours = request.POST.get('worked_hours')
        completion_report = request.POST.get('completion_report')
        
        task = get_object_or_404(Task, id=task_id)
        
        if task.assigned_to != request.user:
            messages.error(request, "You are not authorized to update this task.")
            return redirect('task_list')
        
        if status == 'completed':
            if not worked_hours or not completion_report:
                messages.error(request, "Worked hours and completion report are required when marking a task as completed.")
                return redirect('task_list')
        
        task.status = status
        
        if worked_hours:
            task.worked_hours = worked_hours
        if completion_report:
            task.completion_report = completion_report
        
        if status == 'in_progress' and not task.started_at:
            task.started_at = timezone.now()
        elif status == 'completed' and not task.completed_at:
            task.completed_at = timezone.now()
            
        task.save()
        
        messages.success(request, "Task status updated successfully.")
        return redirect('task_list')
    
    return redirect('task_list')